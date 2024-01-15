from library.extension import db
from library.library_ma import UserSchema
from library.model import Users
from flask import request
import json
from datetime import datetime
import time

user_schema = UserSchema
users_schema = UserSchema(many=True)

def add_user_service():

    birth_date_str = request.json['birth_date']
    birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())

    username = request.json['username']
    email = request.json['email']
    password_hash = request.json['password_hash']
    description = request.json['description']
    nickname = request.json['nickname']
    birth_date = birth_date_timestamp
    avatar = request.json['avatar']
    cover_photo = request.json['cover_photo']
    gender = request.json['gender']
    role = request.json['role']
    create_at = int(time.time())
    try:
        new_user = Users(username, email, password_hash, description, nickname,
                 birth_date, avatar, cover_photo, gender, role, create_at)
        db.session.add(new_user)
        db.session.commit()
        return "Add user success"
    except IndentationError:
        db.session.rollback()
        return "Can not add user"

