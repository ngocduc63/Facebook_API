import math
from facebook.facebook_ma import UserSchema
from facebook.model import Users, TokenBlocklist, Likes, Posts, Comments
from ..extension import (my_json, obj_success_paginate)
from ..config import PER_PAGE_LIST_USER
from ..config_error_code import (ERROR_USER_NOT_FOUND, ERROR_USER_HAVE_NOT_ROLE, ERROR_DATA_NOT_MATCH,
                                 ERROR_NOT_FOUND_EMAIL, ERROR_PASSWORD_NOT_MATCH, ERROR_SAVE_DB)
from facebook.extension import db
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from sqlalchemy import func

user_schema = UserSchema()
users_schema = UserSchema(many=True)


def check_role_admin(current_user):
    user = db.session.query(Users).filter(Users.id == current_user.id).first()

    # role 1 la admin
    if user and user.role == 1:
        return True
    else:
        return False


def admin_login_service():
    data = request.json

    if not (data and ('email' in data) and ('password' in data)):
        return my_json(ERROR_DATA_NOT_MATCH)

    email_data = data['email']
    password_data = data["password"]

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


def get_all_user_service(page, current_user):
    if not check_role_admin(current_user):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    users = Users.query.paginate(page=page, per_page=PER_PAGE_LIST_USER, error_out=False)

    cur_page = users.page
    max_page = math.ceil(users.total / PER_PAGE_LIST_USER)

    if users:
        users_data = users_schema.dump(users)
        return my_json(obj_success_paginate(users_data, cur_page, max_page))
    else:
        return my_json(ERROR_USER_NOT_FOUND)


def block_user_by_id_service(user_id, current_user):
    if not check_role_admin(current_user):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    user = db.session.query(Users).filter(Users.id == user_id, Users.is_block == 0).first()

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    try:
        user.is_block = 1

        db.session.commit()
        return my_json(f"block user {user_id} success")
    except Exception as e:
        print(e)
        return my_json(ERROR_SAVE_DB)


def unblock_user_by_id_service(user_id, current_user):
    if not check_role_admin(current_user):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    user = db.session.query(Users).filter(Users.id == user_id, Users.is_block == 1).first()

    if not user:
        return my_json(ERROR_USER_NOT_FOUND)

    try:
        user.is_block = 0

        db.session.commit()
        return my_json(f"unblock user {user_id} success")
    except Exception as e:
        print(e)
        return my_json(ERROR_SAVE_DB)


def block_list_user_by_id_service(current_user):
    if not check_role_admin(current_user):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    data = request.json
    check_data = data and ('list_id' in data)

    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    list_id = data['list_id']

    for user_id in list_id:
        user = db.session.query(Users).filter(Users.id == user_id, Users.is_block == 0).first()
        if not user:
            return my_json(ERROR_USER_NOT_FOUND)
        try:
            user.is_block = 1

            db.session.commit()
        except Exception as e:
            print(e)
            return my_json(ERROR_SAVE_DB)

    return my_json(f"block users success")


def count_user_for_year(year):
    rs = []
    for month in range(1, 13):
        start_date = datetime(year, month, 1).timestamp()
        if month < 12:
            end_date = datetime(year, month + 1, 1).timestamp()
        else:
            end_date = datetime(year + 1, 1, 1).timestamp()

        count_user = db.session.query(Users).filter(Users.create_at >= start_date, Users.create_at < end_date).count()

        rs.append(count_user)

    return rs


def count_post_for_year(year):
    rs = []
    for month in range(1, 13):
        start_date = datetime(year, month, 1).timestamp()

        if month < 12:
            end_date = datetime(year, month + 1, 1).timestamp()
        else:
            end_date = datetime(year + 1, 1, 1).timestamp()

        count_post = db.session.query(Posts).filter(Posts.create_at >= start_date, Posts.create_at < end_date).count()
        rs.append(count_post)

    return rs


def statistical_service(current_user):
    if not check_role_admin(current_user):
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    num_user = db.session.query(Users).count()
    num_user_male = db.session.query(Users).filter(Users.gender == 1).count()
    num_user_female = db.session.query(Users).filter(Users.gender == 2).count()
    num_post = db.session.query(Posts).count()
    num_like = db.session.query(Likes).count()
    num_comment = db.session.query(Comments).count()

    current_year = datetime.now().year
    users_created_per_month = count_user_for_year(current_year)
    posts_created_per_month = count_post_for_year(current_year)

    result = {
        'current_year': current_year,
        'num_user': num_user,
        'num_user_male': num_user_male,
        'num_user_female': num_user_female,
        'num_post': num_post,
        'num_like': num_like,
        'num_comment': num_comment,
        'list_count_user': users_created_per_month,
        'list_count_post': posts_created_per_month,
    }

    return my_json(result)
