from flask import Flask, render_template, jsonify, request, redirect, Response
import subprocess
import json
import atexit
import os
import sys
import random
import tempfile
import webbrowser
import time

from data import load_customer_data, clean_response
from data import Customers, TwoFactCode
from data import GRADES, GRADE_SECONDARY_POS, GRADE_SECONDARY_NEG, PHONES_EXAMPLES #phone_nums_example
from llm import sentiment_analysis
    
# initialize the temporary code & subprocess
customers = Customers([])
two_fact_code = TwoFactCode('000000')
active_process = None

# Add at the top with other globals
grading_results = None

# delete file storing temporary code when program ends
def cleanup():
    """ delete temporary code file """
    try:
        if os.path.exists("2fa_code.json"):
            os.remove("2fa_code.json")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# register the cleanup function
atexit.register(cleanup)

def resource_path(relative_path):
    """ get absolute path to resource """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# begin the retrieving transcript subprocess
def fetch_transcript():
    """ begin the retrieving transcript subprocess """
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

# Set the secret key for session management
app.secret_key = os.urandom(24)

@app.route('/')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/transcripts')
def transcripts():
    return render_template('transcripts.html')

@app.route('/transcript-result')
def transcript_result():
    # Load test transcript data
    with open('sample_data/sample_transcripts.json', 'r', encoding='utf-8') as f:
        test_transcripts = json.load(f)
    
    # Create a list of dictionaries with the required format
    transcripts_data = []
    for transcript in test_transcripts:
        transcripts_data.append({
            'customer': transcript['customer'],
            'transcript': transcript['transcript']
        })
    
    return render_template('transcript_result.html', transcripts=transcripts_data)

@app.route('/run-script', methods=['POST'])
def run():
    # customers.set_phone_nums(PHONES_EXAMPLES)

    global active_process
    # start the subprocess and store it
    active_process = fetch_transcript()
    return jsonify({"needs_2fa": True})

@app.route('/fetch-transcripts', methods=['POST'])
def fetch_transcripts():
    global active_process
        
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
    
    # Read output line by line
    while True:
        line = active_process.stdout.readline()
        if not line:
            break
            
        if line.startswith("FETCH_PROGRESS:"):
            # Just continue - we don't need to handle progress updates here
            continue
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
    transcripts = [t[1:] for t in transcripts]
    
    # Return transcripts
    # return jsonify({
    #     "status": "fetch_complete",
    #     "transcripts": transcripts,
    #     "total": len(transcripts)
    # })

    # Create a list of dictionaries with the required format
    transcripts_data = []
    for transcript in transcripts:
        transcripts_data.append({
            'customer': transcript['customer'],
            'transcript': transcript['transcript']
        })
    
    return render_template('transcript_result.html', transcripts=transcripts_data)

@app.route('/grade-transcripts', methods=['POST'])
def grade_transcripts():
    global grading_results
    # Get transcripts from request
    transcripts = request.json.get('transcripts', [])
    if not transcripts:
        return jsonify({"error": "No transcripts provided"}), 400
        
    phone_nums = customers.get_phone_nums()
    
    # Use transcript length and check for mismatch
    total_count = len(transcripts)  # Use transcript length instead of phone number count
    if total_count != customers.get_len_phone_nums():
        print(f"Warning: Mismatch between number of transcripts ({total_count}) and phone numbers ({customers.get_len_phone_nums()})")
    
    def generate():
        results = []
        gradable_count = sum(1 for t in transcripts if not t.startswith('FAILED'))
        
        for i in range(total_count):
            # Send progress update
            yield f"PROGRESS:{i+1}/{total_count}\n"
            
            if not transcripts[i].startswith('FAILED'):
                grade = random.choice(GRADES)
                grade_secondary = "" #random.choice(["Booked", "Spam"])
                # # simulate grade time
                time.sleep(0.5)
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

        # Store results globally
        global grading_results
        grading_results = {
            "output": results,
            "gradable_count": gradable_count,
            "failed_count": total_count - gradable_count
        }
        
        # Send completion signal
        yield "DONE\n"

    return Response(generate(), mimetype='text/plain')

@app.route('/grade-result')
def grade_result():
    if not grading_results:
        return redirect('/transcripts')
    return render_template('grade_result.html', results=grading_results)

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

@app.route('/loading')
def loading():
    return render_template('loading.html')

if __name__ == '__main__':
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