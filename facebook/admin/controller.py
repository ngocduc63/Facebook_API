from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import (get_all_user_service, block_user_by_id_service, statistical_service,
                       block_list_user_by_id_service, unblock_user_by_id_service, unblock_list_user_by_id_service,
                       get_all_post_service)

admin = Blueprint("admin", __name__)


@admin.route("/admin/get-all-user", methods=["POST"])
@jwt_required()
def get_all_user():
    return get_all_user_service(current_user)


@admin.route("/admin/block-user/<int:user_id>", methods=["PUT"])
@jwt_required()
def block_user_by_id(user_id):
    return block_user_by_id_service(user_id, current_user)


@admin.route("/admin/unblock-user/<int:user_id>", methods=["PUT"])
@jwt_required()
def unblock_user_by_id(user_id):
    return unblock_user_by_id_service(user_id, current_user)


@admin.route("/admin/block-users", methods=["PUT"])
@jwt_required()
def block_users_by_id():
    return block_list_user_by_id_service(current_user)


@admin.route("/admin/unblock-users", methods=["PUT"])
@jwt_required()
def unblock_users_by_id():
    return unblock_list_user_by_id_service(current_user)


@admin.route("/admin/statistical", methods=["GET"])
@jwt_required()
def statistical():
    return statistical_service(current_user)


@admin.route("/admin/get-all-post/<int:page>", methods=["GET"])
@jwt_required()
def get_all_post(page):
    return get_all_post_service(page, current_user)
