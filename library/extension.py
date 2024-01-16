from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import jsonify
import json

db = SQLAlchemy()
ma = Marshmallow()


def my_json(data=None, error_code=0, mess="fail"):
    if error_code == 0:
        rs = {
            "errorCode": 0,
            "message": "success",
            "data": data
        }
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