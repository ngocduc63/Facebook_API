from flask import Blueprint
from .services import add_user_service, get_user_by_id_service, get_all_user_service

users = Blueprint("users", __name__)

@users.route("/get-all-user")
def get_all_user():
    return get_all_user_service()
@users.route("/user-management/user", methods = ["POST"])
def add_user():
    return add_user_service()

@users.route("/user-management/user/<int:id>", methods = ["GET"])
def get_user_by_id(id):
    return get_user_by_id_service(id)
