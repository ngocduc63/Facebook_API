from flask import Blueprint
from .services import (add_user_service, get_user_by_id_service, get_all_user_service,
                       update_profile_by_id_service, block_user_by_id_service, search_user_service,
                       user_login_service, upload_avatar_service, get_avatar_from_filename_service,
                       upload_cover_photo_service, get_cover_photo_from_filename_service, logout_user, refresh_service
                       )
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity

users = Blueprint("users", __name__)


@users.route("/user-management/user/get-all-user/<int:page>", methods=["GET"])
@jwt_required()
def get_all_user(page):
    claims = get_jwt()

    return get_all_user_service(page, claims)


@users.route("/user-management/user/search", methods=["GET"])
@jwt_required()
def search_user():
    return search_user_service()


@users.route("/user-management/user/register", methods=["POST"])
def add_user():
    return add_user_service()


@users.route("/user-management/user/login", methods=["POST"])
def user_login():
    return user_login_service()


@users.route("/user-management/user/refresh", methods=["POST"])
@jwt_required(refresh=True)
def user_refresh():
    identity = get_jwt_identity()
    return refresh_service(identity)


@users.route("/user-management/user/<int:user_id>", methods=["POST"])
@jwt_required()
def get_user_by_id(user_id):
    return get_user_by_id_service(user_id)


@users.route("/user-management/user/update", methods=["PUT"])
@jwt_required()
def update_profile_by_id():
    return update_profile_by_id_service(current_user)


@users.route("/user-management/user/block/<int:user_id>", methods=["PUT"])
@jwt_required()
def block_user_by_id(user_id):
    claims = get_jwt()
    return block_user_by_id_service(user_id, claims)


@users.route("/user-management/user/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    return upload_avatar_service(current_user)


@users.route("/user-management/user/cover", methods=["POST"])
@jwt_required()
def upload_cover_photo():
    return upload_cover_photo_service(current_user)


@users.route("/user-management/user/avatar/<string:filename>", methods=["GET"])
def get_avatar(filename):
    return get_avatar_from_filename_service(filename)


@users.route("/user-management/user/cover/<string:filename>", methods=["GET"])
def get_cover_photo(filename):
    return get_cover_photo_from_filename_service(filename)


@users.route("/user-management/user/logout", methods=["POST"])
@jwt_required(verify_type=False)
def user_logout():
    claims = get_jwt()
    return logout_user(claims)
