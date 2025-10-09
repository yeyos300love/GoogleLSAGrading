from flask import Blueprint, Response, render_template, stream_with_context, redirect, url_for, jsonify, request
from app.models import PipelineJob, Lead
from app.services.podium_client import podium_subprocess
from app import db
import json

bp = Blueprint('jobs', __name__)

active_drivers = {}

@bp.route('/') # default route
@bp.route('/list-jobs')
def list_jobs():
    jobs = PipelineJob.query.order_by(
        PipelineJob.id.asc() #desc()
    ).all()
    return render_template('jobs/list.html', jobs=jobs)

@bp.route('/job/<int:job_id>')
def detail(job_id):
    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)
    leads = Lead.query.filter_by(job_id=job_id).all()

    # calculate number of leads leftto analyze
    analyzed_count = Lead.query.filter_by(job_id=job_id, status='analyzed').count()

    return render_template('jobs/detail.html', job=job, customers=leads, analyzed_count=analyzed_count)

@bp.route('/<int:job_id>/start-podium')
def start_podium(job_id):
    """user clicks 'Fetch Transcripts' - starts podium"""
    
    driver = podium_subprocess()
    active_drivers[f'podium_{job_id}'] = driver
    
    return render_template('jobs/podium.html')#, job=job)


@bp.route('/<int:job_id>/submit-2fa', methods=['POST'])
def submit_2fa(job_id):
    """user submitted 2FA code"""
    code = request.json.get('code')
    driver = active_drivers.get(f'podium_{job_id}')


@bp.route('/<int:job_id>/analyze-all', methods=['POST'])
def analyze_all(job_id):
    return render_template('dashboard/loading.html', job_id=job_id, action='analyze')

@bp.route('/<int:job_id>/analyze-all-stream', methods=['GET'])
def analyze_all_stream(job_id):
    return Response(stream_with_context(analyze_stream(job_id)), mimetype='text/event-stream')

def analyze_stream(job_id):
    job = PipelineJob.query.get_or_404(job_id)
    #job = db.session.get(PipelineJob, job_id) instead of PipelineJob.query.get(job_id)
    
    # Get only leads that are transcript_fetched and don't start with FAILED
    leads = Lead.query.filter_by(job_id=job_id, status='transcript_fetched').all()
    leads_to_analyze = [lead for lead in leads if not lead.transcript.startswith('FAILED')]

    total = len(leads_to_analyze)
    
    if total == 0:
        yield f"data: {json.dumps({'message': 'No transcripts to analyze', 'done': True})}\n\n"
        return

    for i, lead in enumerate(leads_to_analyze, 1):
        # Send progress update
        yield f"data: {json.dumps({'message': f'Let me analyze those transcripts...({i}/{total})', 'progress': i, 'total': total})}\n\n"
        
        # TODO: Perform your actual analysis here
        # Example: lead.grade = analyze_transcript(lead.transcript)
        # lead.status = 'analyzed'
        print(str(i)+'.', 'Grading:', lead.phone)
        #db.session.commit()
    
    # Check if all leads are analyzed
    all_leads = Lead.query.filter_by(job_id=job_id).all()
    if all(lead.status == 'analyzed' for lead in all_leads):
        job.status = 'analyzed'
        #db.session.commit()
    
    # Send completion
    yield f"data: {json.dumps({'done': True, 'redirect': url_for('jobs.detail', job_id=job_id)})}\n\n"


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
    leads_by_phone = {lead.phone: lead for lead in leads}

    # update each lead
    for update in updates:
        phone = update['phone']
        if phone in leads_by_phone:
            lead = leads_by_phone[phone]
            lead.grade = update['grade']
            lead.grade_secondary = update['grade_secondary']
            lead.status = 'analyzed'

    # check if all leads are analyzed, if so update job status
    if all(lead.status == 'analyzed' for lead in leads):
        job.status = 'analyzed'
    
    # commit all changes
    db.session.commit()
    
    return redirect(url_for('jobs.detail', job_id=job_id))


@bp.route('/<int:job_id>/save-transcript', methods=['POST'])
def save_transcript(job_id):
    #job = PipelineJob.query.get_or_404(job_id)
    
    print("Form data:", request.form)  # Debug lin

    phone = request.form.get('phone')
    transcript = request.form.get('transcript')
    
    if not phone or transcript is None:
        return jsonify({'success': False, 'error': 'Missing phone or transcript'}), 400
    
    # Find the lead by phone number
    lead = Lead.query.filter_by(job_id=job_id, phone=phone).first()
    
    if not lead:
        return jsonify({'success': False, 'error': 'Lead not found'}), 404
    
    # Update the transcript
    lead.transcript = transcript
    db.session.commit()
    
    return redirect(url_for('jobs.detail', job_id=job_id, reopen=phone))
