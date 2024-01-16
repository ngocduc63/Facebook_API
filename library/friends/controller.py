from flask import Blueprint
from .services import add_friend_service, get_friend_by_id_service, get_all_friend_service

friends = Blueprint("friends", __name__)

@friends.route("/get-all-friend")
def get_all_user():
    return get_all_friend_service()
@friends.route("/friend-management/friend", methods = ["POST"])
def add_user():
    return add_friend_service()

@friends.route("/friend-management/friend/<int:id>", methods = ["GET"])
def get_user_by_id(id):
    return get_friend_by_id_service(id)
