import math
from sqlalchemy import func, text
from library.extension import db
from library.facebook_ma import UserSchema
from library.model import Users
from flask import request, jsonify
from datetime import datetime
import time
from ..extension import my_json, obj_success, obj_success_paginate
from unidecode import unidecode
from ..config import PER_PAGE_USER

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def add_user_service():
    data = request.json
    check_data = (data and ('username' in data) and ('email' in data) and
                  ('password_hash' in data) and ('birth_date' in data) and ('gender' in data))

    if check_data:
        try:
            birth_date_str = data['birth_date']
            birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())
        except Exception as e:
            print(e)
            return my_json(error_code=4, mess="error date not match")

        username = data['username']
        email = data['email']
        password_hash = data['password_hash']
        description = ""
        nickname = ""
        birth_date = birth_date_timestamp
        avatar = ""
        cover_photo = ""
        gender = data['gender']
        role = 1
        create_at = int(time.time())
        try:
            new_user = Users(username, email, password_hash, description, nickname,
                             birth_date, avatar, cover_photo, gender, role, create_at)
            db.session.add(new_user)
            db.session.commit()
            return my_json(user_schema.dump(new_user))
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
        except Exception as e:
            print(e)
            # return my_json(error_code=2, mess="error data not match")

    else:
        return my_json(error_code=3, mess="error validate data")


def get_user_by_id_service(user_id):
    user = Users.query.get(user_id)

    if user:
        user_data = user_schema.dump(user)
        return jsonify(obj_success(user_data))
    else:
        return my_json(error_code=1, mess="Not found user")


def get_all_user_service(page):
    users = Users.query.paginate(page=page, per_page=PER_PAGE_USER, error_out=False)

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_USER)

    if users:
        users_data = users_schema.dump(users)
        return jsonify(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(error_code=1, mess="Not found user")


def update_profile_by_id_service(user_id):
    user = Users.query.get(user_id)
    data = request.json

    if not user:
        return my_json(error_code=1, mess="Not found user")

    if (data and ('username' in data) and ('description' in data) and ('nickname' in data)
            and ('birth_date' in data) and ('gender' in data)):

        try:
            birth_date_str = data['birth_date']
            birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())
        except Exception as e:
            print(e)
            return my_json(error_code=4, mess="error date not match")

        try:
            user.username = data['username']
            user.description = data['description']
            user.nickname = data['nickname']
            user.birth_date = birth_date_timestamp
            user.gender = data['gender']
            db.session.commit()
            users_data = user_schema.dump(user)
            return jsonify(obj_success(users_data))
        except Exception as e:
            print(e)
            return my_json(error_code=3, mess="error in DB")
    else:
        return my_json(error_code=2, mess="Data user not match")


def delete_user_by_id_service(user_id):
    user = Users.query.get(user_id)

    if not user:
        return my_json(error_code=1, mess="Not found user")

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify(obj_success({}))
    except Exception as e:
        print(e)
        return my_json(error_code=3, mess="error in DB")


def search_approximate(array, key, value):
    result = [obj for obj in array if unidecode(value.lower()) in unidecode(obj[key].lower())]
    return result


def search_user_service():

    data = request.json
    if not data and ("page" in data) and ("username" in data):
        return my_json(error_code=2, mess="data not match")

    page = data['page']
    username_input = data['username']

    users = (Users.query.filter(func.lower(Users.username).ilike(f'%{username_input.lower()}%'))
             .paginate(page=page, per_page=PER_PAGE_USER, error_out=False))

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_USER)

    if users:
        users_data = users_schema.dump(users)
        # search_approximate(users_data, "username", username_input)

        return jsonify(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(error_code=1, mess="Not found user")


def user_login_service():
    data = request.json

    if not data and ('email' in data) and ('password' in data):
        return my_json(error_code=1, mess="data not match")

    email_data = data['email']
    user = Users.query.filter(text("(users.email) = (:email)")).params(email=email_data).first()
    user_data = user_schema.dump(user)

    if not user_data:
        return my_json(error_code=2, mess="email not found")

    if not user_data['password_hash'] == data['password']:
        return my_json(error_code=3, mess="password fail")

    return my_json(user_data)
