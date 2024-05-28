import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
SQLALCHEMY_DATABASE_UR = os.environ.get("DATABASE_URL")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
SQLALCHEMY_TRACK_MODIFICATIONS = False
PER_PAGE_LIST_USER = 10
PER_PAGE_LIST_FRIEND = 10
PER_PAGE_POST = 10
PER_PAGE_LIKE_POST = 10
PER_PAGE_COMMENT_POST = 10
MESSAGE_FETCH_LIMIT = 20
LIST_ROOM_CHAT_FETCH_LIMIT = 20
ADD_FRIEND_FETCH_LIMIT = 10
NOTIFICATION_FETCH_LIMIT = 10
CONNECT_MONGO_PRODUCT = \
    'mongodb+srv://admin:0918273645abc@facebook.7yqdc0f.mongodb.net/?retryWrites=true&w=majority&appName=facebook'
CONNECT_MONGO_DEV = \
    'mongodb+srv://ducdotb63:0918273645abc@facebook.hltsvun.mongodb.net/?retryWrites=true&w=majority&appName=Facebook'
