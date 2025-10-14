from app import db

class Lead(db.Model):
    __tablename__ = 'lead_records'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('pipeline_jobs.id'), nullable=False)
    phone = db.Column(db.String(50))
    received = db.Column(db.String(25)) #db.DateTime, nullable=True)

    # pending, transcript_fetched, analyzed, completed, failed
    status = db.Column(db.String(25), default='pending')  
    
    transcript = db.Column(db.Text, nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    grade_secondary = db.Column(db.Text, nullable=True) #db.String(100), nullable=True)
