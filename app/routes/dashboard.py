from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import InternalServerError
from app import db
from app.services.csv_processor import process_csv_upload
from app.models import PipelineJob, Lead
import os

bp = Blueprint('dashboard', __name__)

@bp.route('/') # default route
def index():
    
    return render_template('dashboard/index.html')

@bp.route('/upload-csv', methods=['POST'])
def upload():
    if 'file' not in request.files:
        raise InternalServerError("No file provided")

    file = request.files['file']
    if file.filename == '':
        raise InternalServerError("No file selected")

    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    customers_leads = process_csv_upload(filepath)
    #print(customers_leads)

    # create job
    job = PipelineJob(csv_filename=filename, total_records=len(customers_leads), status='pending')
    db.session.add(job)
    db.session.commit()
    # create customer records
    for lead, received in customers_leads:
        # check if lead with same phone already exists for this job
        existing_lead = Lead.query.filter_by(job_id=job.id, phone=lead).first()
        if existing_lead:
            transcript = "WARNING • Duplicate customer\nThis is a duplicate lead."
            db.session.add(Lead(job_id=job.id, phone=lead, received=received, status='transcript_fetched', transcript=transcript))
        else:
            db.session.add(Lead(job_id=job.id, phone=lead, received=received, status='pending'))
    db.session.commit()

    return redirect(url_for('jobs.detail', job_id=job.id))
    #return render_template('dashboard/index.html')
    