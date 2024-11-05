from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room
from .chat.db_chat import get_room_collection

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on('create_room_call')
def handel_create_room_call(data):
    join_room(f'call_{data["room"]}')
    data_room = get_room_collection(data['room'])
    if not data_room:
        socketio.emit('room_call_notification', 'join_room_fail', room=f'call_{data["room"]}')
        return

    user_key = data_room['users']['username_key']
    friend_data = data_room['users']['username_friend']
    if user_key['user_id'] == data['user_id']:
        send_for = friend_data
        send_by = user_key
    else:
        send_for = user_key
        send_by = friend_data

    send_by['type'] = 'call'
    send_by['room'] = data['room']
    send_by['signalData'] = data['signalData']
    socketio.emit('join_notification', send_by, room=f'user_id_{send_for["user_id"]}')


@socketio.on('join_room_call')
def handel_join_room_call(data):
    join_room(f'call_{data["room"]}')
    socketio.emit('room_call_notification', data, room=f'call_{data["room"]}')


@socketio.on('room_call_data')
def handel_send_data_call():
    socketio.emit('room_call_data')


@socketio.on('leave_room_call')
def handel_leave_room_call(data):
    leave_room(f'call_{data["room"]}')
    data['type'] = 'end_call'
    socketio.emit('room_call_notification', data, room=f'call_{data["room"]}')
