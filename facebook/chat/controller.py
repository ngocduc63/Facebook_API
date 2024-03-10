from ..extension import get_current_time
from .db_chat import (save_room, add_room_members, get_rooms_for_user, get_room, is_room_member, add_room_member,
                      get_room_members, update_room, remove_room_members, save_message, get_messages)
from flask_socketio import SocketIO, join_room, leave_room


def socket_handel(socketio):
    @socketio.on('send_message')
    def handle_send_message_event(data):
        data['created_at'] = get_current_time().strftime("%d %b, %H:%M")
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


def create_room(room_name, user_id_create, user_id_added):
    if len(room_name) and user_id_added and user_id_create:
        room_id = save_room(room_name, user_id_create)
        add_room_member(room_id, room_name, user_id_added, user_id_create)
        return True
    else:
        return False


def view_messages_room(room_id, user_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, user_id):
        messages = get_messages(room_id)
        return messages
    else:
        return None
