from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import jsonify

db = SQLAlchemy()
ma = Marshmallow()


def my_json(data=None, error_code=0, mess="fail"):
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
