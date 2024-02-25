import math

from sqlalchemy import func, text
from library.extension import db
from library.facebook_ma import UserSchema, PostSchema
from library.model import Users, Posts
from flask import request, jsonify, send_from_directory
from datetime import datetime
from ..extension import (my_json, obj_success, obj_success_paginate, allowed_file,
                         get_current_time, get_path_upload, get_path_local)
from unidecode import unidecode
from ..config import PER_PAGE_USER
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token

UPLOAD_AVATAR_FOLDER = "upload/avatar"
UPLOAD_COVER_PHOTO_FOLDER = "upload/cover_photo"

user_schema = UserSchema()
post_schema = PostSchema()
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
        description = ""
        nickname = ""
        birth_date = birth_date_timestamp
        avatar = ""
        cover_photo = ""
        gender = data['gender']
        role = 0
        create_at = get_current_time()
        try:
            new_user = Users(username, email, description, nickname,
                             birth_date, avatar, cover_photo, gender, role, create_at)

            new_user.set_password(password=data['password_hash'])
            db.session.add(new_user)
            db.session.commit()
            return my_json(user_schema.dump(new_user))
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
        except Exception as e:
            print(e)
            return my_json(error_code=2, mess="error email existed or er db")

    else:
        return my_json(error_code=3, mess="error validate data")


def get_user_by_id_service(user_id):
    user = Users.query.get(user_id)

    if user:
        user_data = user_schema.dump(user)
        return jsonify(obj_success(user_data))
    else:
        return my_json(error_code=1, mess="Not found user")


def get_all_user_service(page, claims):

    if claims["is_staff"]:
        return my_json(error_code=2, mess="User not admin")

    users = Users.query.paginate(page=page, per_page=PER_PAGE_USER, error_out=False)

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_USER)

    if users:
        users_data = users_schema.dump(users)
        return jsonify(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(error_code=1, mess="Not found")


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

    if not user.check_password(password=data["password"]):
        return my_json(error_code=3, mess="password fail")

    access_token = create_access_token(user_data)

    rs = {
        "errorCode": 0,
        "message": "success",
        "data": user_data,
        "access_token": access_token
    }
    return jsonify(rs)


def change_name_file(filename, user_id):
    name = f"{filename.split('.')[0]}_{user_id}_{str(get_current_time())}"
    return f"{name}.{filename.split('.')[1]}"


def upload_avatar_service(user_id):
    data = request.files
    user = Users.query.get(user_id)

    if not user:
        return my_json(error_code=3, mess="not found user")

    if not data:
        return my_json(error_code=1, mess="not found data request")

    file = data['file']
    if file.filename == '':
        return my_json(error_code=2, mess="file null")

    if file and allowed_file(file.filename):
        try:
            filename_full = secure_filename(file.filename)
            filename = change_name_file(filename_full, user_id)
            file.save(get_path_upload(UPLOAD_AVATAR_FOLDER, filename))

            # set avatar
            user.avatar = filename

            # add post
            title = f"{user.username} đã cập nhật ảnh đại diện của {"anh ấy" if user.gender == 1 else "cô ấy"}"
            post_new = Posts(title, filename, user.id, 1, 0, get_current_time())
            db.session.add(post_new)

            # save db
            db.session.commit()
            users_data = user_schema.dump(user)
            post_data = post_schema.dump(post_new)
            return jsonify(obj_success({"user": users_data, "post": post_data}))
        except Exception as e:
            print(e)
            return my_json(error_code=4, mess="error save data")


def upload_cover_photo_service(user_id):
    data = request.files
    user = Users.query.get(user_id)

    if not user:
        return my_json(error_code=3, mess="not found user")

    if not data:
        return my_json(error_code=1, mess="not found data request")

    file = data['file']
    if file.filename == '':
        return my_json(error_code=2, mess="file null")

    if file and allowed_file(file.filename):
        try:
            filename_full = secure_filename(file.filename)
            filename = change_name_file(filename_full, user_id)
            file.save(get_path_upload(UPLOAD_COVER_PHOTO_FOLDER, filename))

            # set avatar
            user.cover_photo = filename

            # add post
            title = f"{user.username} đã cập nhật ảnh bìa của {"anh ấy" if user.gender == 1 else "cô ấy"}"
            post_new = Posts(title, filename, user.id, 1, 0, get_current_time())
            db.session.add(post_new)

            # save db
            db.session.commit()
            users_data = user_schema.dump(user)
            post_data = post_schema.dump(post_new)
            return jsonify(obj_success({"user": users_data, "post": post_data}))
        except Exception as e:
            print(e)
            return my_json(error_code=4, mess="error save data")


def get_avatar_from_filename_service(filename):
    return send_from_directory(get_path_local(UPLOAD_AVATAR_FOLDER), filename)


def get_cover_photo_from_filename_service(filename):
    return send_from_directory(get_path_local(UPLOAD_COVER_PHOTO_FOLDER), filename)
