from flask import Blueprint
from .services import (create_notification_add_friend_service, get_notification_add_friend_service
                       )
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity
from facebook.socketio_instance import socketio
from flask_socketio import join_room, leave_room

notifications = Blueprint("notifications", __name__)


# api
@notifications.route("/notification-management/add-friend/<int:page>", methods=["GET"])
@jwt_required()
def get_notification_add_friend(page):
    return get_notification_add_friend_service(current_user, page)


# socket
@socketio.on('join_notification_post')
def handle_join_post_notification_event(data):
    join_room(f'post_{data['post_id']}')
    socketio.emit('notification_post', {}, room=f'post_{data['post_id']}')


@socketio.on('join_notification')
def handle_join_post_notification_event(data):
    join_room(f'user_id_{data['user_id']}')
    socketio.emit('join_notification', "listen event add friend success", room=f'user_id_{data['user_id']}')


@socketio.on('leave_notification_post')
def handle_leave_post_notification_event(data):
    leave_room(f'post_{data['post_id']}')
    socketio.emit('notification_post', {}, room=f'post_{data['post_id']}')
