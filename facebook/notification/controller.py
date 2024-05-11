from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import get_notifications_for_user_service

notifications = Blueprint("notifications", __name__)


# api
@notifications.route("/notification-management/notifications/<int:page>", methods=["GET"])
@jwt_required()
def get_notifications_for_user(page):
    return get_notifications_for_user_service(current_user, page)

