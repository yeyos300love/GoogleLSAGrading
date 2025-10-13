from flask import Blueprint, Response, render_template, stream_with_context, redirect, url_for, jsonify, request, current_app
from datetime import datetime
from app.models import PipelineJob, Lead
from app.services.podium_client import start_podium_subprocess, perform_verification, continue_podium_subprocess, search_number
from app.services.sentiment_analyzer import analyze_sentiment
from app.services.glsa_client import start_glsa_subprocess, continue_glsa_subprocess, get_final_index, fill_form
from app import db
import threading
import json


bp = Blueprint('jobs', __name__)

active_drivers = {}
driver_lock = threading.Lock()


# -------------------------------------- display all jobs --------------------------------------
@bp.route('/') # default route
@bp.route('/list-jobs')
def list_jobs():
    jobs = PipelineJob.query.order_by(
        PipelineJob.id.desc() #asc()
    ).all()
    return render_template('jobs/list.html', jobs=jobs)

# -------------------------------------- display individual job details --------------------------------------
@bp.route('/job/<int:job_id>')
def detail(job_id):
    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)
    leads = Lead.query.filter_by(job_id=job_id).all()

    # calculate number of leads analyzed
    analyzed_count = Lead.query.filter_by(job_id=job_id, status='analyzed').count()
    # calculate number of lead transcript fetched
    fetched_count = Lead.query.filter_by(job_id=job_id, status='transcript_fetched').count()
    # calculate number of lead transcript fetched
    completed_count = Lead.query.filter_by(job_id=job_id, status='completed').count()

    return render_template('jobs/detail.html', job=job, customers=leads, 
                                                analyzed_count=analyzed_count,
                                                fetched_count=fetched_count,
                                                completed_count=completed_count)


# -------------------------------------- loading messages --------------------------------------
@bp.route('/<int:job_id>/loading')
def loading(job_id):
    action = request.args.get('action')#, 'fetch-transcripts')
    return render_template('dashboard/loading.html', job_id=job_id, action=action)


# -------------------------------------- fetch transcripts --------------------------------------
@bp.route('/<int:job_id>/start-podium', methods=['POST'])
def start_podium(job_id):
    """user clicks 'Fetch Transcripts' - starts podium"""
    job = PipelineJob.query.get_or_404(job_id)
    app = current_app._get_current_object()

    def run_podium():
        with app.app_context():
            driver = start_podium_subprocess()
            with driver_lock:
                active_drivers[f'podium_{job_id}'] = driver
            print(f"Driver stored for job {job_id}")

    # start background thread
    # redirect immediatley while target starts/runs in the background
    threading.Thread(target=run_podium, daemon=True).start()
    
    return render_template('jobs/podium.html', job=job)

@bp.route('/<int:job_id>/submit-2fa', methods=['POST'])
def submit_2fa(job_id):
    """user submitted 2FA code"""
    code = request.json.get('code')
    print(f'we recieved this: {code}')
    
    # Use lock to safely retrieve the driver
    with driver_lock:
        driver = active_drivers.get(f'podium_{job_id}')

    perform_verification(driver, code)

    #return redirect(url_for('jobs.loading', job_id=job_id), action='fetch-transcripts')
    #return Response(stream_with_context(fetching_stream(job_id)), mimetype='text/event-stream')
    return jsonify({'success': True})

@bp.route('/<int:job_id>/fetch-transcripts-stream', methods=['GET'])
def fetch_transcripts_stream(job_id):
    return Response(stream_with_context(fetching_stream(job_id)), mimetype='text/event-stream')

def fetching_stream(job_id):
    job = PipelineJob.query.get_or_404(job_id)

    with driver_lock:
        driver = active_drivers.get(f'podium_{job_id}')

    continue_podium_subprocess(driver)

    # get only leads that are pending
    leads = Lead.query.filter_by(job_id=job_id, status='pending').all()

    total = len(leads)
    
    if total == 0:
        yield f"data: {json.dumps({'message': 'No transcripts to fetch', 'done': True})}\n\n"
        return

    for i, lead in enumerate(leads, 1):
        # Send progress update
        yield f"data: {json.dumps({'message': f'Let me fetch those transcripts...({i}/{total})', 'progress': i, 'total': total})}\n\n"

        #import time
        #time.sleep(1)
        print(str(i)+'.', 'Fetching:', lead.phone)

        transcript = search_number(driver, lead.phone)
        lead.transcript = transcript
        lead.status = 'transcript_fetched'
        db.session.commit()  

    # check if all leads are transcript_fetched, if so update job status
    # get all leads for this job
    leads = Lead.query.filter_by(job_id=job_id).all()
    if all(lead.status == 'transcript_fetched' for lead in leads):
        job.status = 'transcripts_fetched'  
        db.session.commit()

    # send completion
    yield f"data: {json.dumps({'done': True, 'redirect': url_for('jobs.detail', job_id=job_id)})}\n\n"


# -------------------------------------- sentiment analysis --------------------------------------
@bp.route('/<int:job_id>/analyze-all', methods=['POST'])
def analyze_all(job_id):
    #return render_template('dashboard/loading.html', job_id=job_id, action='analyze-all')
    return redirect(url_for('jobs.loading', job_id=job_id, action='analyze-all'))

@bp.route('/<int:job_id>/analyze-all-stream', methods=['GET'])
def analyze_all_stream(job_id):
    return Response(stream_with_context(analyze_stream(job_id)), mimetype='text/event-stream')

def analyze_stream(job_id):
    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)
    
    # get only leads that are transcript_fetched and don't start with FAILED
    leads = Lead.query.filter_by(job_id=job_id, status='transcript_fetched').all()
    leads_to_analyze = [lead for lead in leads if not lead.transcript.startswith('FAILED')]

    total = len(leads_to_analyze)
    
    if total == 0:
        yield f"data: {json.dumps({'message': 'No transcripts to analyze', 'done': True})}\n\n"
        return

    for i, lead in enumerate(leads_to_analyze, 1):
        # Send progress update
        yield f"data: {json.dumps({'message': f'Let me analyze those transcripts...({i}/{total})', 'progress': i, 'total': total})}\n\n"
        
        #import time
        #time.sleep(0.25)
        print(str(i)+'.', 'Grading:', lead.phone)

        grade, grade_secondary = analyze_sentiment(lead.transcript)
        if grade != 'Not confident':
            lead.status = 'analyzed'
            lead.grade = grade
            lead.grade_secondary = grade_secondary
            db.session.commit()
    
    # check if all leads are analyzed
    all_leads = Lead.query.filter_by(job_id=job_id).all()
    if all(lead.status == 'analyzed' for lead in all_leads):
        job.status = 'analyzed'
        db.session.commit()
    
    # send completion
    yield f"data: {json.dumps({'done': True, 'redirect': url_for('jobs.detail', job_id=job_id)})}\n\n"


# -------------------------------------- glsa form filler --------------------------------------
@bp.route('/<int:job_id>/start-glsa', methods=['POST'])
def start_glsa(job_id):
    """user clicks 'Send to GLSA' button"""
    job = PipelineJob.query.get_or_404(job_id)
    app = current_app._get_current_object()

    def run_glsa():
        with app.app_context():
            driver = start_glsa_subprocess()
            with driver_lock:
                active_drivers[f'glsa_{job_id}'] = driver
            print(f"Driver stored for job {job_id}")

    # start background thread
    # redirect immediatley while target starts/runs in the background
    threading.Thread(target=run_glsa, daemon=True).start()
    
    return render_template('jobs/glsa.html', job=job)

@bp.route('/<int:job_id>/form-completion', methods=['POST'])
def form_completion(job_id):
    return redirect(url_for('jobs.loading', job_id=job_id, action='form-completion'))

@bp.route('/<int:job_id>/form-completion-stream', methods=['GET'])
def form_completion_stream(job_id):
    return Response(stream_with_context(completion_stream(job_id)), mimetype='text/event-stream')

def completion_stream(job_id):

    with driver_lock:
        driver = active_drivers.get(f'glsa_{job_id}')

    dates = [datetime.strptime(lead.received, "%b %d %Y") for lead in Lead.query.filter_by(job_id=job_id).all()]
    start_date = min(dates).strftime("%b %d %Y")
    end_date = max(dates).strftime("%b %d %Y")
    #print(start_date, end_date)

    continue_glsa_subprocess(driver, total_records=Lead.query.filter_by(job_id=job_id).count(), start_date=start_date, end_date=end_date)

    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)

    # get only leads that are analyzed
    leads = Lead.query.filter_by(job_id=job_id, status='analyzed').all()
    total = len(leads)
    
    if total == 0:
        yield f"data: {json.dumps({'message': 'No lead forms to complete', 'done': True})}\n\n"
        return
    
    final_index = get_final_index(len(Lead.query.filter_by(job_id=job_id).all()))

    for i, lead in enumerate(leads, 1):
        # Send progress update
        yield f"data: {json.dumps({'message': f'Let me fill those lead forms...({i}/{total})', 'progress': i, 'total': total})}\n\n"

        print(str(i)+'.', 'Completing Form for:', lead.phone)
        #import time
        #time.sleep(0.25)
        #print(lead.grade, lead.grade_secondary) if lead.grade_secondary else print(lead.grade)
        
        fill_form(driver, lead.grade, lead.grade_secondary, final_index)
        lead.status = 'completed'
        db.session.commit()

    # check if all leads are analyzed
    all_leads = Lead.query.filter_by(job_id=job_id).all()
    if all(lead.status == 'completed' for lead in all_leads):
        job.status = 'completed'
        db.session.commit()

    # send completion
    yield f"data: {json.dumps({'done': True, 'redirect': url_for('jobs.detail', job_id=job_id)})}\n\n"


# -------------------------------------- save table --------------------------------------
@bp.route('/<int:job_id>/save', methods=['POST'])
def save(job_id):
    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)

    updates = request.form.getlist('updates')
    updates = [json.loads(u) for u in updates]
    
    # if no updates, just redirect
    if not updates:
        return redirect(url_for('jobs.detail', job_id=job_id))

    # get all leads for this job
    leads = Lead.query.filter_by(job_id=job_id).all()

    # create a dict for quick phone lookup
    #leads_by_phone = {lead.phone: lead for lead in leads}
    leads_by_id = {lead.id: lead for lead in leads}

    # update each lead
    for update in updates:
        #phone = update['phone']
        #if phone in leads_by_phone:
            #lead = leads_by_phone[phone]
        lead_id = update['lead_id']
        if lead_id in leads_by_id:
            lead = leads_by_id[lead_id]
            lead.grade = update['grade']
            lead.grade_secondary = update['grade_secondary']
            lead.status = 'analyzed'

    # check if all leads are analyzed, if so update job status
    if all(lead.status == 'analyzed' for lead in leads):
        job.status = 'analyzed'
    
    # commit all changes
    db.session.commit()
    
    return redirect(url_for('jobs.detail', job_id=job_id))


# -------------------------------------- save transcript --------------------------------------
@bp.route('/<int:job_id>/save-transcript', methods=['POST'])
def save_transcript(job_id):
    job = PipelineJob.query.get_or_404(job_id)

    #phone = request.form.get('phone')
    lead_id = request.form.get('lead_id')
    transcript = request.form.get('transcript')
    
    if not lead_id or transcript is None:
        return jsonify({'success': False, 'error': 'Missing lead or transcript'}), 400
    
    # find the lead by phone number
    #lead = Lead.query.filter_by(job_id=job_id, phone=phone).first()
    # find the lead by ID (ensures we get the exact lead)
    lead = Lead.query.filter_by(id=lead_id, job_id=job_id).first()
    
    if not lead:
        return jsonify({'success': False, 'error': 'Lead not found'}), 404
    
    # update the transcript
    lead.transcript = transcript
    
    # if status is 'not_fetched', update to 'transcript_fetched'
    if lead.status == 'pending':
        lead.status = 'transcript_fetched'

    # check if all leads are transcript_fetched, if so update job status
    # get all leads for this job
    leads = Lead.query.filter_by(job_id=job_id).all()
    if all(lead.status == 'transcript_fetched' for lead in leads):
        job.status = 'transcripts_fetched'
    
    # for all other statuses, just update the transcript without changing status
    db.session.commit()

    return redirect(url_for('jobs.detail', job_id=job_id, reopen=lead_id))
