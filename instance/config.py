# config.py
import os

SQLALCHEMY_ECHO = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db' 
SQLALCHEMY_TRACK_MODIFICATIONS = False

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

