from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    # load all config settings into Flask
    app.config.from_object(config_class)
    # initialize database extension
    db.init_app(app)

    # register blueprints (routes)
    from app.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app