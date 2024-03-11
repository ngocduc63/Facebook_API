import os

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import jsonify
import time
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'mp4']


def my_json(data=None, error_code=0, mess="error"):
    if error_code == 0:
        rs = obj_success(data)
        return jsonify(rs)
    else:
        rs = {
            "errorCode": error_code,
            "message": mess,
            "data": {}
        }
        return jsonify(rs)


def obj_success(data):
    return {
            "errorCode": 0,
            "message": "success",
            "data": data
        }


def obj_success_paginate(data, cur_page, max_page):
    return {
            "errorCode": 0,
            "message": "success",
            "data": data,
            "currentPage": cur_page,
            "maxPage": max_page
        }


def change_name_file(filename, name_id):
    name = f"{filename.split('.')[0]}_{name_id}_{str(get_current_time())}"
    return f"{name}.{filename.split('.')[1]}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_time():
    return int(time.time())


def get_path_upload(path_name, filename):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path_name, filename)


def get_path_local(path_name):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path_name)


def is_admin(claims):
    if claims["is_staff"]:
        return False
    else:
        return True
