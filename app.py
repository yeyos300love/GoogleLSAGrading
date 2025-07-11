from flask import Flask, render_template, jsonify, request, redirect, Response, stream_with_context
import subprocess
import json
import atexit
import os
import sys
import tempfile
import time
import random
from datetime import datetime

from data import load_customer_data
from data import Customer, Customers, TwoFactCode
from data import GRADES, GRADE_SECONDARY_POS, GRADE_SECONDARY_NEG, PHONES_EXAMPLES #phone_nums_example
from llm import sentiment_analysis
    
# initialize the temporary code & subprocesses
two_fact_code = TwoFactCode('000000')
active_process = None
glsa_process = None
uploaded_filename = None
customers = Customers([])




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
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def update_grades_in_file(phone_nums, grades, grades_secondary):
    """Update the uploaded JSON file with grading results"""
    global uploaded_filename
    
    try:
        file_path = f'data/{uploaded_filename}'
        
        # Load existing data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update grades for each phone number
        for i, phone_number in enumerate(phone_nums):
            # Find existing entry with the same customer phone number
            for entry in data:
                if entry.get("customer") == phone_number:
                    entry["grade"] = grades[i]
                    entry["grade_secondary"] = grades_secondary[i]
                    break
        
        # Save updated data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"ERROR_UPDATING_GRADES: {str(e)}", flush=True)
        return False


def fetch_transcript(filename):
    """ retrieving transcript subprocess """
    podium_script = resource_path('podium.py')
    python_executable = sys.executable
    get_transcript_result = subprocess.Popen([python_executable, podium_script, filename], 
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

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/transcripts')
def transcripts():
    return render_template('transcripts.html')

@app.route('/graded')
def graded():
    return render_template('graded.html')


# update grades when sending to GoogleLSA
@app.route('/update-grades', methods=['POST'])
def update_grades():
    global uploaded_filename
    try:
        updated_grades = request.json.get('grades', [])
        if not updated_grades:
            return jsonify({"error": "No grade data provided"}), 400
        
        # Load the current data from the uploaded file to get phone numbers in the correct order
        file_path = f'data/{uploaded_filename}'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract phone numbers and grades in the same order as the frontend table
        phone_nums = []
        grades = []
        grades_secondary = []
        
        for i, updated_grade in enumerate(updated_grades):
            if i < len(data):
                phone_nums.append(data[i]['customer'])
                grades.append(updated_grade.get('grade', ''))
                grades_secondary.append(updated_grade.get('grade_secondary', ''))
        
        # Use the update_grades_in_file function to update the JSON file
        success = update_grades_in_file(phone_nums, grades, grades_secondary)
        
        if success:
            return jsonify({"success": True, "message": "Grades updated successfully"})
        else:
            return jsonify({"error": "Failed to update grades in file"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# used for dropdown options
@app.route('/options')
def get_options():
    try:
        with open('options.json', 'r') as f:
            options = json.load(f)
        return jsonify(options)
    except Exception as e:
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
        #customers.set_phone_nums(load_customer_data(temp_path))
        customers_found = load_customer_data(temp_path)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create JSON file with uploaded customer data
        current_date = datetime.now()
        date_str = current_date.strftime("%d%b%Y")#.upper()
        json_filename = f"uploaded_{date_str}.json"
        json_filepath = os.path.join('data', json_filename)
        
        global uploaded_filename
        uploaded_filename = json_filename
        
        # Create JSON structure similar to sample_transcripts but with only customer data
        uploaded_data = []
        for phone_number in customers_found:
            uploaded_data.append({
                "customer": phone_number,
                "transcript": "",
                "grade": "",
                "grade_secondary": ""
            })

            customers.add_customer(phone_number)
        
        #print(customers.get_customers())

        # Save to JSON file
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(uploaded_data, f, indent=2)
        
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


@app.route('/run-script', methods=['POST'])
def run():
    global active_process, uploaded_filename
    # start the subprocess and store it
    active_process = fetch_transcript(uploaded_filename)
    return jsonify({"needs_2fa": True})


@app.route('/fetch-transcripts', methods=['POST'])
def fetch_transcripts():
    return Response(stream_with_context(fetch_transcripts_stream()), mimetype='text/event-stream')

def fetch_transcripts_stream():
    global active_process, transcripts_data
        
    if not active_process:
        return jsonify({"error": "No active process found. Please start again."}), 400
        
    # get the code from the user
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "No code provided"}), 400
        
    # update the temporary code file & class
    two_fact_code.update_code(code)
    
    # communicate with the stored process
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
            # Parse and send progress
            parts = line.split(":")[1].strip().split("/")
            current = parts[0].strip()
            total = parts[1].strip()
            yield f"data: {json.dumps({'type': 'fetch_progress', 'current': current, 'total': total})}\n\n"
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

    # Return completion signal
    yield f"data: {json.dumps({'type': 'complete'})}\n\n"


@app.route('/grade-transcripts', methods=['POST'])
def grade_transcripts():
    return Response(stream_with_context(grade_transcripts_stream()), mimetype='text/event-stream')

def grade_transcripts_stream():
    global uploaded_filename

    phone_nums = customers.get_customers()
    #print(phone_nums)
    
    total_count = customers.get_len_customers()

    grades = []
    grades_secondary = []
    
    # Load transcripts from JSON file
    file_path = f'data/{uploaded_filename}'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in range(total_count):
        # Send progress update
        #yield f"PROGRESS:{i+1}/{total_count}\n"
        print(f"PROGRESS:{i+1}/{total_count} - {phone_nums[i]}")
        yield f"data: {json.dumps({'type': 'grading_progress', 'current': i+1, 'total': total_count})}\n\n"
        
        # Find transcript for this phone number
        transcript = ""
        for entry in data:
            if entry.get("customer") == phone_nums[i]:
                transcript = entry.get("transcript", "")
                break
        
        if not transcript.startswith('FAILED'):
            # grade = random.choice(GRADES)
            # grade_secondary = "" #random.choice(["Booked", "Spam"])
            # # simulate grade time
            # time.sleep(0.5)
            grade, grade_secondary = sentiment_analysis(transcript)
        else:
            grade = ""
            grade_secondary = ""

        print(grade, grade_secondary)

        grades.append(grade)
        grades_secondary.append(grade_secondary)

    # Update the uploaded JSON file with grades
    update_grades_in_file(phone_nums, grades, grades_secondary)

    # Send completion signal
    yield "DONE\n"
    yield f"data: {json.dumps({'type': 'complete'})}\n\n"


@app.route('/transcript-result')
def transcript_result():
    global uploaded_filename
    with open(f'data/{uploaded_filename}', 'r', encoding='utf-8') as f:
        test_transcripts = json.load(f)
    
    # Create a list of dictionaries with the required format
    transcripts_data = []
    for transcript in test_transcripts:
        transcripts_data.append({
            'customer': transcript['customer'],
            'transcript': transcript['transcript']
        })
    
    return render_template('transcript_result.html', transcripts=transcripts_data)


@app.route('/grade-result')
def grade_result():
    global uploaded_filename
    with open(f'data/{uploaded_filename}', 'r', encoding='utf-8') as f:
        test_transcripts = json.load(f)

    # Create a list of dictionaries with the required format
    grading_results = []
    for transcript in test_transcripts:
        grading_results.append({
            'phone_number': transcript['customer'],
            'transcript': transcript['transcript'],
            'grade': transcript['grade'],
            'grade_secondary': transcript['grade_secondary']
        })  
    return render_template('grade_result.html', results=grading_results)


@app.route('/glsa')
def glsa():
    global uploaded_filename
    
    with open(f'data/{uploaded_filename}', 'r', encoding='utf-8') as f:
        test_transcripts = json.load(f)

    # Create a list of dictionaries with the required format
    grading_results = []
    for transcript in test_transcripts:
        grading_results.append({
            'phone_number': transcript['customer'],
            'transcript': transcript['transcript'],
            'grade': transcript['grade'],
            'grade_secondary': transcript['grade_secondary']
        })  
        
    return render_template('glsa.html', results=grading_results)


@app.route('/run-glsa', methods=['POST'])
def run_glsa():
    global glsa_process, uploaded_filename
    
    glsa_script = resource_path('glsa.py')
    python_executable = sys.executable
    glsa_process = subprocess.Popen([python_executable, glsa_script, uploaded_filename], 
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
    return jsonify({"success": True})

@app.route('/continue-glsa', methods=['POST'])
def continue_glsa():
    global glsa_process
    if glsa_process and glsa_process.stdin:
        glsa_process.stdin.write('\n')
        glsa_process.stdin.flush()
        return jsonify({"success": True})
    return jsonify({"error": "No active GLSA process"}), 400


@app.route('/stop-glsa', methods=['POST'])
def stop_glsa():
    global glsa_process
    if glsa_process:
        glsa_process.kill()
        glsa_process.wait()
        glsa_process = None
    return jsonify({"success": True, "message": "Grading process stopped"})




@app.route('/transcript-result-test')
def transcript_result_test():
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


@app.route('/graded-result-test')
def graded_result_test():
    # Load test transcript data
    with open('sample_data/sample_transcripts.json', 'r', encoding='utf-8') as f:
        test_transcripts = json.load(f)
    
    # Create a list of dictionaries with the required format
    results = []
    for transcript in test_transcripts:
        results.append({
            'phone_number': transcript['customer'],
            'transcript': transcript['transcript'],
            'grade': transcript['grade'],
            'grade_secondary': transcript['grade_secondary']
        })  

    return render_template('grade_result.html', results=results)


# import webbrowser
# def open_browser():
#     """Wait a second and then open the browser"""
#     time.sleep(1)  # Give the server a second to start
#     webbrowser.open('http://127.0.0.1:5001')

def run_flask():
    """Run the Flask application"""
    app.run(host='0.0.0.0', port=8080) #, debug = True)



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