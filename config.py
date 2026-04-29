import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'tabchem-pharma-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'medicines')
    MEDICINE_IMAGE_SUBDIR = 'uploads/medicines'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
