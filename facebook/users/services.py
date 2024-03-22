import math
from sqlalchemy import func
from facebook.extension import db
from facebook.facebook_ma import UserSchema, PostSchema
from facebook.model import Users, Posts, TokenBlocklist
from flask import request, jsonify, send_from_directory
from datetime import datetime
from ..extension import (my_json, obj_success, obj_success_paginate, allowed_file,
                         get_current_time, get_path_upload, get_path_local,
                         is_admin, change_name_file)
from unidecode import unidecode
from ..config import PER_PAGE_LIST_USER
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, create_refresh_token
import re
from ..config_error_code import (ERROR_DATA_NOT_MATCH, ERROR_FORMAT_EMAIL, ERROR_FORMAT_PASSWORD,
                                 ERROR_FORMAT_DATE, ERROR_NOT_FOUND_EMAIL, ERROR_PASSWORD_NOT_MATCH,
                                 ERROR_USER_NOT_FOUND, ERROR_FILE_NULL, ERROR_UPLOAD_FILE,
                                 ERROR_CHECK_TOKEN,  ERROR_SAVE_DB, ERROR_ACCOUNT_EXIST, ERROR_USER_HAVE_NOT_ROLE)


regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
UPLOAD_AVATAR_FOLDER = "upload/avatar"
UPLOAD_COVER_PHOTO_FOLDER = "upload/cover_photo"

user_schema = UserSchema()
post_schema = PostSchema()
users_schema = UserSchema(many=True)


def add_user_service():
    data = request.json
    check_data = (data and ('username' in data) and ('email' in data) and
                  ('password' in data) and ('birth_date' in data) and ('gender' in data))

    if check_data:
        email = data['email']
        password = data['password']
        if not re.fullmatch(regex_email, email):
            return my_json(ERROR_FORMAT_EMAIL)

        if len(password) < 6:
            return my_json(ERROR_FORMAT_PASSWORD)

        try:
            birth_date_str = data['birth_date']
            birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())
        except Exception as e:
            print(e)
            return my_json(ERROR_FORMAT_DATE)

        username = data['username']
        description = ""
        nickname = ""
        birth_date = birth_date_timestamp
        avatar = "avt_default_male.png" if int(data['gender']) == 1 else "avt_default_female.png"
        cover_photo = ""
        gender = data['gender']
        create_at = get_current_time()
        try:
            new_user = Users(username, email, description, nickname,
                             birth_date, avatar, cover_photo, gender, create_at)

            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return my_json(user_schema.dump(new_user))
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
        except Exception as e:
            print(e)
            return my_json(ERROR_ACCOUNT_EXIST)

    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def get_user_by_id_service(user_id):
    user = Users.query.get(user_id)

    if user:
        user_data = user_schema.dump(user)
        return jsonify(obj_success(user_data))
    else:
        return my_json(ERROR_CHECK_TOKEN)


def get_all_user_service(page, claims):

    if not is_admin(claims):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    users = Users.query.paginate(page=page, per_page=PER_PAGE_LIST_USER, error_out=False)

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_LIST_USER)

    if users:
        users_data = users_schema.dump(users)
        return my_json(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(ERROR_USER_NOT_FOUND)


def update_profile_by_id_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    user = Users.query.get(user_id)
    data = request.json

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    if (data and ('username' in data) and ('description' in data) and ('nickname' in data)
            and ('birth_date' in data) and ('gender' in data)):

        try:
            birth_date_str = data['birth_date']
            birth_date_timestamp = int(datetime.strptime(birth_date_str, '%m/%d/%Y').timestamp())
        except Exception as e:
            print(e)
            return my_json(ERROR_FORMAT_DATE)

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
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def block_user_by_id_service(user_id, claims):
    user = Users.query.get(user_id)

    if not is_admin(claims):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    try:
        user.is_block = 1

        jti = claims['jti']
        token_b = TokenBlocklist(jti=jti)
        token_b.save()

        db.session.commit()
        return my_json(f"block user {user_id} success")
    except Exception as e:
        print(e)
        return my_json(ERROR_SAVE_DB)


def search_approximate(array, key, value):
    result = [obj for obj in array if unidecode(value.lower()) in unidecode(obj[key].lower())]
    return result


def search_user_service():

    data = request.json
    if not data and ("page" in data) and ("username" in data):
        return my_json(ERROR_DATA_NOT_MATCH)

    page = data['page']
    username_input = data['username']

    users = (Users.query.filter(func.lower(Users.username).ilike(f'%{username_input.lower()}%'))
             .paginate(page=page, per_page=PER_PAGE_LIST_USER, error_out=False))

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_LIST_USER)

    if users:
        users_data = users_schema.dump(users)
        # search_approximate(users_data, "username", username_input)

        return jsonify(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(ERROR_USER_NOT_FOUND)


def refresh_service(identity):
    new_access_token = create_access_token(identity=identity)
    return my_json({"access_token": new_access_token})


def user_login_service():
    data = request.json

    if not (data and ('email' in data) and ('password' in data)):
        return my_json(ERROR_DATA_NOT_MATCH)

    email_data = data['email']
    password_data = data["password"]

    if not re.fullmatch(regex_email, email_data):
        return my_json(ERROR_FORMAT_EMAIL)

    if len(password_data) < 6:
        return my_json(ERROR_FORMAT_PASSWORD)

    user = db.session.query(Users).filter(Users.email == email_data).first()
    user_data = user_schema.dump(user)

    if not user_data:
        return my_json(ERROR_NOT_FOUND_EMAIL)

    if user.is_block == 1:
        return my_json(ERROR_USER_NOT_FOUND)

    if not user.check_password(password=password_data):
        return my_json(ERROR_PASSWORD_NOT_MATCH)

    access_token = create_access_token(user_data["email"])
    refresh_token = create_refresh_token(user_data["email"])

    rs = {
        "errorCode": 0,
        "message": "success",
        "data": user_data,
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }
    return jsonify(rs)


def upload_avatar_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.files
    user = Users.query.get(user_id)

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    if not data:
        return my_json(ERROR_DATA_NOT_MATCH)

    file = data['file']
    if file.filename == '':
        return my_json(ERROR_FILE_NULL)

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
            return my_json(ERROR_UPLOAD_FILE)


def upload_cover_photo_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.files
    user = Users.query.get(user_id)

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    if not data:
        return my_json(ERROR_DATA_NOT_MATCH)

    file = data['file']
    if file.filename == '':
        return my_json(ERROR_FILE_NULL)

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
            return my_json(ERROR_SAVE_DB)


def get_avatar_from_filename_service(filename):
    return send_from_directory(get_path_local(UPLOAD_AVATAR_FOLDER), filename)


def get_cover_photo_from_filename_service(filename):
    return send_from_directory(get_path_local(UPLOAD_COVER_PHOTO_FOLDER), filename)


def logout_user(claims):
    print(claims)
    type_token = claims['type']
    jti = claims['jti']

    if type_token == 'refresh' and jti:
        token_b = TokenBlocklist(jti=jti)
        token_b.save()
        return my_json("logout success")
    else:
        return my_json(ERROR_CHECK_TOKEN)
