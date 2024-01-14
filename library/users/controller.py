from flask import Blueprint

users = Blueprint("users", __name__)

@users.route("/get-all-user")
def get_all_user():
    return "all user"