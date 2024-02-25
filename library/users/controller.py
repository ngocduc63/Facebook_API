from flask import Blueprint
from .services import (add_user_service, get_user_by_id_service, get_all_user_service,
                       update_profile_by_id_service, delete_user_by_id_service, search_user_service,
                       user_login_service, upload_avatar_service, get_avatar_from_filename_service,
                       upload_cover_photo_service, get_cover_photo_from_filename_service
                       )
from flask_jwt_extended import jwt_required, get_jwt

users = Blueprint("users", __name__)


@users.route("/user-management/user/get-all-user/<int:page>")
@jwt_required()
def get_all_user(page):
    claims = get_jwt()

    return get_all_user_service(page, claims)


@users.route("/user-management/user/search/", methods=["GET"])
@jwt_required()
def search_user():
    return search_user_service()


@users.route("/user-management/user/register", methods=["POST"])
def add_user():
    return add_user_service()


@users.route("/user-management/user/login", methods=["GET"])
def user_login():
    return user_login_service()


@users.route("/user-management/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    return get_user_by_id_service(user_id)


@users.route("/user-management/user/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_profile_by_id(user_id):
    return update_profile_by_id_service(user_id)


@users.route("/user-management/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user_by_id(user_id):
    return delete_user_by_id_service(user_id)


@users.route("/user-management/user/avatar/<int:user_id>", methods=["POST"])
@jwt_required()
def upload_avatar(user_id):
    return upload_avatar_service(user_id)


@users.route("/user-management/user/cover/<int:user_id>", methods=["POST"])
@jwt_required()
def upload_cover_photo(user_id):
    return upload_cover_photo_service(user_id)


@users.route("/user-management/user/avatar/<string:filename>", methods=["GET"])
@jwt_required()
def get_avatar(filename):
    return get_avatar_from_filename_service(filename)


@users.route("/user-management/user/cover/<string:filename>", methods=["GET"])
@jwt_required()
def get_cover_photo(filename):
    return get_cover_photo_from_filename_service(filename)
