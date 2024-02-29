from flask import Blueprint
from .services import add_friend_service, get_friend_by_id_service, unfriend_service

friends = Blueprint("friends", __name__)


@friends.route("/friend-management/add-friend", methods=["POST"])
def add_friend():
    return add_friend_service()


@friends.route("/friend-management/unfriend", methods=["DELETE"])
def unfriend():
    return unfriend_service()


@friends.route("/friend-management/friend/<int:user_id>", methods=["GET"])
def get_friend_by_id(user_id):
    return get_friend_by_id_service(user_id)
