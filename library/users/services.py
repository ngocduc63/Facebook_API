from library.extension import db
from library.facebook_ma import UserSchema
from library.model import Users
from flask import request, jsonify
from datetime import datetime
import time

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def add_user_service():
    data = request.json
    check_data = (data and ('username' in data) and ('email' in data) and
                  ('password_hash' in data) and ('description' in data) and ('nickname' in data) and
                  ('birth_date' in data) and ('avatar' in data) and ('cover_photo' in data) and
                  ('gender' in data) and ('role' in data)
                  )

    if check_data:

        birth_date_str = data['birth_date']
        birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())

        username = data['username']
        email = data['email']
        password_hash = data['password_hash']
        description = data['description']
        nickname = data['nickname']
        birth_date = birth_date_timestamp
        avatar = data['avatar']
        cover_photo = data['cover_photo']
        gender = data['gender']
        role = data['role']
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

    else:
        return "Request error"



def get_user_by_id_service(id):
    user = Users.query.get(id)

    if user:
        return user_schema.jsonify(user)
    else:
        return "Not found user"


def get_all_user_service():
    users = Users.query.all()

    if users:
        return users_schema.jsonify(users)
    else:
        return "Not found user"
