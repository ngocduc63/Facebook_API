from .db_chat import (save_room, add_room_members, get_rooms_for_user, get_room, is_room_member, add_room_member,
                      get_room_members, update_room, remove_room_members, save_message, get_messages)
from ..config_error_code import ERROR_CHECK_TOKEN, ERROR_DATA_NOT_MATCH, ERROR_FOUND_ROOM_CHAT
from ..extension import my_json, obj_message_paginate
from flask import request
from facebook.model import Friends, Users
from facebook.extension import db
from facebook.facebook_ma import FriendSchema, UserSchema

friend_schema = FriendSchema()
user_schema = UserSchema()


def create_room(room_name, user_id_create, user_id_added):
    if len(room_name) and user_id_added and user_id_create:
        room_id = save_room(room_name, user_id_create)
        add_room_member(room_id, room_name, user_id_added, user_id_create)
        return room_id
    else:
        return None


def get_messages_room_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.json
    check_data = data and ('room_id' in data) and ('page' in data)

    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    room_id = data['room_id']
    page = data['page']

    friend = db.session.query(Friends).filter(Friends.id_room_chat == room_id).first()
    friend = friend_schema.dump(friend)
    friend_id = friend['friend_id'] if friend['user_id'] == user_id else friend['user_id']
    friend_data = db.session.query(Users).filter(Users.id == friend_id).first()
    friend_data = user_schema.dump(friend_data)

    room = get_room(room_id)
    if room and is_room_member(room_id, user_id):
        messages, total_page = get_messages(room_id, page - 1)
        return my_json(obj_message_paginate(messages, friend_data, page, total_page))
    else:
        return my_json(ERROR_FOUND_ROOM_CHAT)


def data_notification_mess(room_id, user_id):
    friend = db.session.query(Friends).filter(Friends.id_room_chat == room_id).first()
    friend = friend_schema.dump(friend)
    friend_id = friend['friend_id'] if friend['user_id'] == user_id else friend['user_id']
    user_data = db.session.query(Users).filter(Users.id == user_id).first()
    user_data = user_schema.dump(user_data)
    return {
        'room': room_id,
        'friend': user_data
    }, friend_id

