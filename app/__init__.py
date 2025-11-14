from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    # load all config settings into Flask
    app.config.from_object(config_class)
    
    # initialize database extension
    db.init_app(app)

    # Create upload folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # register blueprints (routes)
    from app.routes import dashboard_bp, jobs_bp, settings_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)#, url_prefix='/job')
    app.register_blueprint(settings_bp)

    # create database tables
    with app.app_context():
        db.create_all()

        # Initialize default prompt if none exists
        from app.models import SystemPrompt
        if not SystemPrompt.query.first():
            default_prompt = SystemPrompt(prompt_text=app.config['DEFAULT_SYSTEM_PROMPT'])
            db.session.add(default_prompt)
            db.session.commit()

    # error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app