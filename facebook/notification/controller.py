from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import get_notifications_for_user_service
from facebook.socketio_instance import socketio
from flask_socketio import join_room, leave_room

notifications = Blueprint("notifications", __name__)


# api
@notifications.route("/notification-management/notifications/<int:page>", methods=["GET"])
@jwt_required()
def get_notifications_for_user(page):
    return get_notifications_for_user_service(current_user, page)


# socket
@socketio.on('join_notification')
def handle_join_notification_event(data):
    join_room(f'user_id_{data["user_id"]}')
    socketio.emit('join_notification', "listen event for user success", room=f'user_id_{data["user_id"]}')


@socketio.on('leave_notification')
def handle_leave_notification_event(data):
    leave_room(f'user_id_{data["user_id"]}')
    socketio.emit('join_notification', "leave event for user success", room=f'user_id_{data["user_id"]}')