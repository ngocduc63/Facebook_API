from .db_chat import (save_room, add_room_members, get_rooms_for_user, get_room, is_room_member, add_room_member,
                      get_room_members, update_room, remove_room_members, save_message, get_messages)
from flask_socketio import join_room, leave_room
from datetime import datetime
from facebook.socketio_instance import socketio
from flask import Blueprint
from .services import get_messages_room_service
from flask_jwt_extended import jwt_required, current_user

chats = Blueprint("chat", __name__)


# api
@chats.route("/chat-management/room", methods=["POST"])
@jwt_required()
def add_friend():
    return get_messages_room_service(current_user)


# socket
@socketio.on('send_message')
def handle_send_message_event(data):
    data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_message(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])






