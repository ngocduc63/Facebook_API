from flask import Blueprint
from .services import (add_friend_service, get_friend_by_id_service, unfriend_service, accept_service,
                       get_invite_by_id_service, get_room_chat_service, search_invite_service, search_friend_service)
from flask_jwt_extended import jwt_required, get_jwt, current_user

friends = Blueprint("friends", __name__)


@friends.route("/friend-management/add-friend/<int:friend_id>", methods=["POST"])
@jwt_required()
def add_friend(friend_id):
    return add_friend_service(friend_id, current_user)


@friends.route("/friend-management/accept/<int:friend_id>", methods=["PUT"])
@jwt_required()
def accept_friend(friend_id):
    return accept_service(friend_id, current_user)


@friends.route("/friend-management/unfriend/<int:friend_id>", methods=["DELETE"])
@jwt_required()
def unfriend(friend_id):
    return unfriend_service(friend_id, current_user)


@friends.route("/friend-management/friend/<int:page>", methods=["GET"])
@jwt_required()
def get_friend_by_id(page):
    return get_friend_by_id_service(page, current_user)


@friends.route("/friend-management/invite-friend/<int:page>", methods=["GET"])
@jwt_required()
def get_invite_by_id(page):
    return get_invite_by_id_service(page, current_user)


@friends.route("/friend-management/get-room/<int:friend_id>", methods=["GET"])
@jwt_required()
def get_room_chat(friend_id):
    return get_room_chat_service(current_user, friend_id)


@friends.route("/friend-management/search-invite", methods=["POST"])
@jwt_required()
def search_invite_friend():
    return search_invite_service(current_user)


@friends.route("/friend-management/search-friend", methods=["POST"])
@jwt_required()
def search_friend():
    return search_friend_service(current_user)
