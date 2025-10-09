from app import db

class PipelineJob(db.Model):
    __tablename__ = 'pipeline_jobs'

    id = db.Column(db.Integer, primary_key=True)
    csv_filename = db.Column(db.String(255), nullable=False)
    total_records = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')
    # pending, transcripts_fetched, analyzed, completed
    
    # relationship
    leads = db.relationship('Lead', backref='job', lazy=True, cascade='all, delete-orphan')