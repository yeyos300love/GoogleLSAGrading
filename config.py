import os

class Config:
    # secrets
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pipeline.db'

    # file uploads
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'csv'}