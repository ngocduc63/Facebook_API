from library.extension import db
from library.facebook_ma import UserSchema
from library.model import Users
from flask import request, jsonify
from datetime import datetime
import time
from ..extension import my_json, obj_success

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
            return my_json(data)
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
        except Exception:
            return my_json(error_code=2, mess="error data not match")

    else:
        return my_json(error_code=3, mess="error validate data")


def get_user_by_id_service(id):
    user = Users.query.get(id)

    if user:
        user_data = user_schema.dump(user)
        return jsonify(obj_success(user_data))
    else:
        return my_json(error_code=1, mess="Not found user")


def get_all_user_service():
    users = Users.query.all()

    if users:
        users_data = users_schema.dump(users)
        return jsonify(obj_success(users_data))
    else:
        return my_json(error_code=1, mess="Not found user")
