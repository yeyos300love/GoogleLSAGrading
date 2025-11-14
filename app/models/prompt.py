from app import db

class SystemPrompt(db.Model):
    __tablename__ = 'system_prompts'

    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
