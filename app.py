from flask import Flask, render_template, jsonify, request, Response
import subprocess
import json
import atexit
import os
import sys
import random
import tempfile
import webbrowser
import queue
#import threading
import time

from data import load_customer_data, clean_response, GRADES, GRADE_SECONDARY_POS, GRADE_SECONDARY_NEG, PHONES_EXAMPLES #phone_nums_example
from llm import sentiment_analysis

# Add a queue for fetch progress
fetch_progress_queue = queue.Queue()

class TwoFactCode:
    def __init__(self, code):
        """Initialize with a code."""
        self.code = code

    def get_code(self):
        """Return the stored code."""
        return self.code
    
    def update_code(self, new_code):
        self.code = new_code
        with open("2fa_code.json", "w") as f:
            json.dump({"code": self.code}, f)  # Save to a file

class Customers:
    def __init__(self, phone_nums):
        self.phone_nums = phone_nums

    def set_phone_nums(self, phone_nums):
        self.phone_nums = phone_nums

    def get_len_phone_nums(self):
        return len(self.phone_nums)
    
    def get_phone_nums(self):
        return self.phone_nums
    
class TestDataUse:
    def __init__(self, test_bool):
        self.test_bool = test_bool

    def set_testdata_bool(self, test_bool):
        self.test_bool = test_bool

    def get_testdata_bool(self):
        return self.test_bool
    
# initialize the temporary code & subprocess
customers = Customers([])
two_fact_code = TwoFactCode('000000')
active_process = None
use_test_data = TestDataUse(True)

# create file to store temporary code, delete it when program ends
def cleanup():
    try:
        if os.path.exists("2fa_code.json"):
            os.remove("2fa_code.json")
    except Exception as e:
        print(f"Error during cleanup: {e}")
# register the cleanup function
atexit.register(cleanup)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# begin the retrieving transcript subprocess
def fetch_transcript():
    podium_script = resource_path('podium.py')
    python_executable = sys.executable
    get_transcript_result = subprocess.Popen([python_executable, podium_script] + customers.get_phone_nums(), 
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
    return get_transcript_result



app = Flask(__name__,
           template_folder=resource_path('templates'),
           static_folder=resource_path('static')) # initialize app

@app.route('/')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run():
    if use_test_data.get_testdata_bool():
         return jsonify({"needs_2fa": True})
    
    elif not use_test_data.get_testdata_bool():
        # Check if we have customer data from file upload
        if customers.get_len_phone_nums() > 0:
            # Use uploaded customer data
            #phone_nums = customers.get_phone_nums()
            print('file was uploaded')
        else:
            # Use example data when Run Grader was clicked
            customers.set_phone_nums(PHONES_EXAMPLES)
            #phone_nums = customers.get_phone_nums()
            # load the test transcripts
            #with open('sample_data/test_transcript.json', 'r', encoding='utf-8') as f:
            #    transcripts = json.load(f)
            #time.sleep(1)

        global active_process
        # start the subprocess and store it
        active_process = fetch_transcript()
        return jsonify({"needs_2fa": True})

@app.route('/grade-progress')
def grade_progress():
    def generate():
        yield f"data: 1\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/fetch-progress')
def fetch_progress():
    def generate():
        try:
            progress = fetch_progress_queue.get(timeout=1)
            return f"data: {progress}\n\n"
        except queue.Empty:
            return f"data: \n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/submit-2fa', methods=['POST'])
def submit_2fa():
    if use_test_data.get_testdata_bool():
        # Check for phase - if it's the grading phase, process the transcripts
        if request.json.get('phase') == 'grade':
            transcripts = request.json.get('transcripts')
            phone_nums = customers.get_phone_nums() if customers.get_len_phone_nums() > 0 else PHONES_EXAMPLES
            total_count = len(phone_nums)
            
            results = []
            for i in range(total_count):
                grade = random.choice(GRADES)
                
                if grade == 'Very satisfied' or grade == 'Somewhat satisfied':
                    grade_secondary = random.choice(GRADE_SECONDARY_POS)
                elif grade == 'Very dissatisfied' or grade == 'Somewhat dissatisfied':
                    grade_secondary = random.choice(GRADE_SECONDARY_NEG)
                else:
                    grade_secondary = ''

                # simulate grade time
                time.sleep(0.5)

                results.append({
                    "phone_number": phone_nums[i],
                    "grade": grade,
                    "grade_secondary": grade_secondary,
                    "transcript": transcripts[i]
                })
            
            return jsonify({
                "output": results,
                "use_test_data": True
            })
        else:
            # Initial 2FA submission - just send back the transcripts after fetch
            if customers.get_len_phone_nums() > 0:
                # use uploaded customer data
                phone_nums = customers.get_phone_nums()
                transcripts = ['test'] * len(phone_nums)
            else:
                # use example data when Run Grader was clicked
                phone_nums = PHONES_EXAMPLES
                # load the test transcripts
                test_path = resource_path('sample_data/test_transcript_long.json') #'sample_data/test_transcript.json'
                with open(test_path, 'r', encoding='utf-8') as f:
                    transcripts = json.load(f)

            return jsonify({
                "status": "fetch_complete",
                "transcripts": transcripts
            })

    elif not use_test_data.get_testdata_bool():
        global active_process
        
        # Check for phase - if we're in the initial fetch phase
        if not request.json.get('phase') == 'grade':
            if not active_process:
                return jsonify({"error": "No active process found. Please start again."}), 400
                
            # get the code from the user
            code = request.json.get('code')
            if not code:
                return jsonify({"error": "No code provided"}), 400
                
            # update the temporary code file & class
            two_fact_code.update_code(code)
            
            # communicate with the stored process
            transcripts = []
            current_output = ""
            
            # Send the code to the process
            active_process.stdin.write(code + "\n")
            active_process.stdin.flush()
            
            # Read output line by line to track progress
            while True:
                line = active_process.stdout.readline()
                if not line:
                    break
                    
                if line.startswith("FETCH_PROGRESS:"):
                    # Extract progress and add to queue
                    progress = line.strip().split(": ")[1]
                    fetch_progress_queue.put(progress)
                elif line.startswith("Enter temporary code:"):
                    continue
                else:
                    current_output += line
            
            # Get any remaining output
            remaining_output, _ = active_process.communicate()
            current_output += remaining_output
            
            # clean up the output
            current_output = current_output.strip()
            
            # clear the process after we're done
            active_process = None

            # split transcripts and filter out empty strings while preserving formatting
            transcripts = [t for t in current_output.split('-' * 25) if t]
            transcripts = [t[1:] for t in transcripts] # remove first character of first item
            
            # Return just the transcripts after fetch completes
            return jsonify({
                "status": "fetch_complete",
                "transcripts": transcripts 
            })
            
        # Grading phase processing
        else:
            # Get transcripts from request
            transcripts = request.json.get('transcripts', [])
            if not transcripts:
                return jsonify({"error": "No transcripts provided"}), 400
                
            phone_nums = customers.get_phone_nums()
            #print(len(transcripts), len(phone_nums))
            
            # Use transcript length and check for mismatch
            total_count = len(transcripts)  # Use transcript length instead of phone number count
            if total_count != customers.get_len_phone_nums():
                print(f"Warning: Mismatch between number of transcripts ({total_count}) and phone numbers ({customers.get_len_phone_nums()})")
            
            results = []
            #if len(transcripts) == customers.get_len_phone_nums():
            
            for i in range(total_count):
                #print(transcripts[i])
                
                if not transcripts[i].startswith('FAILED'):
                    grade = random.choice(GRADES)
                    grade_secondary = "" #random.choice(["Booked", "Spam"])
                    # # simulate grade time
                    # time.sleep(0.5)
                    #grade, grade_secondary = clean_response(sentiment_analysis(transcripts[i]))
                else:
                    grade = ""
                    grade_secondary = ""

                

                results.append({
                    "phone_number": phone_nums[i] if i < len(phone_nums) else "Unknown",  # Handle potential mismatch
                    "grade": grade,
                    "grade_secondary": grade_secondary,
                    "transcript": transcripts[i]
                })
            
            return jsonify({"output": results})
            
    try:
        pass
    except Exception as e:
        active_process = None  # Clean up on error
        print(f"Error occurred: {str(e)}") 
        return jsonify({"error": str(e)}), 500

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV"}), 400
    
    try:
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'uploaded.csv')
        
        # Save the uploaded file
        file.save(temp_path)
        
        # Load customer data from the temporary file
        customers.set_phone_nums(load_customer_data(temp_path))
        
        # Clean up: remove temporary file and directory
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        if not customers:
            return jsonify({"error": "No customer data found in CSV"}), 400
        
        return jsonify({
            "success": True,
            "message": "I was able to read that no problem!",
            #"customer_count": len(customers),
            "needs_2fa": True
        })
        
    except Exception as e:
        # Ensure cleanup happens even if there's an error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        return jsonify({"error": str(e)}), 500

@app.route('/check-test-data')
def check_test_data():
    return jsonify({"use_test_data": use_test_data.get_testdata_bool()})

@app.route('/reset-customers', methods=['POST'])
def reset_customers():
    global customers
    customers = Customers([])  # reset the customers instance to an empty array
    return jsonify({"success": True, "message": "Customers reset successfully."})

@app.route('/options')
def get_options():
    try:
        with open('options.json', 'r') as f:
            options = json.load(f)
        return jsonify(options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def open_browser():
    """Wait a second and then open the browser"""
    time.sleep(1)  # Give the server a second to start
    webbrowser.open('http://127.0.0.1:5001')

def run_flask():
    """Run the Flask application"""
    app.run(host='0.0.0.0', port=8080) #, debug = True)

if __name__ == '__main__':
    use_test_data.set_testdata_bool(False)
    run_flask()
    #open_browser()

    # # start the Flask app in a separate thread
    # flask_thread = threading.Thread(target=run_flask)
    # flask_thread.daemon = True  # make the thread daemon so it closes with the main program
    # flask_thread.start()

    # # open the browser in another thread
    # browser_thread = threading.Thread(target=open_browser)
    # browser_thread.daemon = True
    # browser_thread.start()

    # # keep the main thread running
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     sys.exit(0)