from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity
from .services import get_all_user_service, block_user_by_id_service, admin_login_service, statistical_service

admin = Blueprint("admin", __name__)


@admin.route("/admin/login", methods=["POST"])
def user_login():
    return admin_login_service()


@admin.route("/admin/get-all-user/<int:page>", methods=["GET"])
@jwt_required()
def get_all_user(page):
    return get_all_user_service(page, current_user)


@admin.route("/admin/block-user/<int:user_id>", methods=["PUT"])
@jwt_required()
def block_user_by_id(user_id):
    return block_user_by_id_service(user_id, current_user)


@admin.route("/admin/statistical", methods=["GET"])
@jwt_required()
def statistical():
    return statistical_service()
