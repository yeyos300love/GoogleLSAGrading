from app.models import SystemPrompt
from app import db
from flask import Blueprint, render_template, jsonify, request, current_app

bp = Blueprint('settings', __name__)

@bp.route('/') # default route
@bp.route('/list-options')
def list_options():
    return render_template('settings/options.html')

@bp.route('/get-prompt')
def get_prompt():
    prompt = SystemPrompt.query.first()
    return jsonify({'prompt': prompt.prompt_text if prompt else current_app.config['DEFAULT_SYSTEM_PROMPT']})
    
@bp.route('/save-prompt', methods=['POST'])
def save_prompt():
    prompt_text = request.form.get('prompt')
    prompt = SystemPrompt.query.first()
    prompt.prompt_text = prompt_text
    db.session.commit()
    return jsonify({'success': True})
