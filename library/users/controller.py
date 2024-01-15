from flask import Blueprint
from .services import add_user_service

users = Blueprint("users", __name__)

@users.route("/get-all-user")
def get_all_user():
    return "all user"
@users.route("/user-management/user", methods = ["POST"])
def add_user():
    return add_user_service()