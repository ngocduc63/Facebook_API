import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
SQLALCHEMY_DATABASE_UR = os.environ.get("DATABASE_URL")
SQLALCHEMY_DATABASE_URI = "sqlite:///facebook.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False