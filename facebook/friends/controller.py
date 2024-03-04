from flask import Blueprint
from .services import add_friend_service, get_friend_by_id_service, unfriend_service
from flask_jwt_extended import jwt_required, get_jwt, current_user

friends = Blueprint("friends", __name__)


@friends.route("/friend-management/add-friend/<int:friend_id>", methods=["POST"])
@jwt_required()
def add_friend(friend_id):
    return add_friend_service(friend_id, current_user)


@friends.route("/friend-management/unfriend/<int:friend_id>", methods=["DELETE"])
@jwt_required()
def unfriend(friend_id):
    return unfriend_service(friend_id, current_user)


@friends.route("/friend-management/friend/<int:user_id>", methods=["GET"])
@jwt_required()
def get_friend_by_id(user_id):
    return get_friend_by_id_service(user_id)
