from flask import Blueprint
from .services import (add_user_service, get_user_by_id_service, get_all_user_service,
                       update_profile_by_id_service, delete_user_by_id_service, search_user_service,
                       user_login_service, upload_avatar_service, get_image_service
                       )

users = Blueprint("users", __name__)


@users.route("/user-management/user/get-all-user/<int:page>")
def get_all_user(page):
    return get_all_user_service(page)


@users.route("/user-management/user/search/", methods=["GET"])
def search_user():
    return search_user_service()


@users.route("/user-management/user/register", methods=["POST"])
def add_user():
    return add_user_service()


@users.route("/user-management/user/login", methods=["GET"])
def user_login():
    return user_login_service()


@users.route("/user-management/user/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    return get_user_by_id_service(user_id)


@users.route("/user-management/user/<int:user_id>", methods=["PUT"])
def update_profile_by_id(user_id):
    return update_profile_by_id_service(user_id)


@users.route("/user-management/user/<int:user_id>", methods=["DELETE"])
def delete_user_by_id(user_id):
    return delete_user_by_id_service(user_id)


@users.route("/user-management/user/avatar/<int:user_id>", methods=["POST"])
def upload_avatar(user_id):
    return upload_avatar_service(user_id)


@users.route("/user-management/user/avatar/<string:filename>", methods=["GET"])
def get_avatar(filename):
    return get_image_service(filename)
