import math
from facebook.extension import db
from facebook.facebook_ma import FriendSchema, UserSchema
from facebook.model import Friends, Users
from flask import request
from ..extension import my_json, obj_success_paginate, get_current_time
from ..config import PER_PAGE_LIST_FRIEND
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased
from ..chat.services import create_room
from ..config_error_code import (ERROR_SAVE_DB,  ERROR_FRIEND_NOT_FOUND, ERROR_CAN_NOT_ADD_FRIEND,
                                 ERROR_CAN_NOT_ADD_YOURSELF, ERROR_CAN_NOT_CREATE_ROOM, ERROR_PAGE_NUM_NULL,
                                 ERROR_CHECK_TOKEN, ERROR_DATA_NOT_MATCH, ERROR_USER_NOT_FOUND)
from ..socketio_instance import socketio
from ..notification.db_notification import add_notification_collection

friend_schema = FriendSchema()
user_schema = UserSchema()
friends_schema = FriendSchema(many=True)
user_alias = aliased(Users)
friend_alias = aliased(Users)


def notification_for_add_friend(current_user, friend_id, new_friend, create_at):
    data_notification = {
        'description': f'{current_user.username} đã gửi lời mời kết bạn cho bạn',
        'created_by': {
            'id': current_user.id,
            'username': current_user.username,
            'avatar': current_user.avatar
        },
        'for_user_id': friend_id,
        'id': new_friend.id,
        'create_at': create_at
    }

    id_notification = add_notification_collection(friend_id, data_notification, 1)
    if id_notification:
        socketio.emit('join_notification', data_notification, room=f'user_id_{friend_id}')


def notification_for_accept_friend(current_user, friend_id):
    data_notification = {
        'description': f'{current_user.username} đã đồng ý kết bạn',
        'created_by': {
            'id': current_user.id,
            'username': current_user.username,
            'avatar': current_user.avatar
        },
        'for_user_id': friend_id,
        'id_friend': current_user.id,
        'create_at': get_current_time()
    }

    id_notification = add_notification_collection(friend_id, data_notification, 2)
    if id_notification:
        socketio.emit('join_notification', data_notification, room=f'user_id_{friend_id}')


def add_friend_service(friend_id, current_user):
    user_id = current_user.id
    friend_id = friend_id

    if user_id == friend_id:
        return my_json(ERROR_CAN_NOT_ADD_YOURSELF)

    check_friend = db.session.query(Users).filter(Users.id == friend_id).first()

    if not check_friend:
        return my_json(ERROR_USER_NOT_FOUND)

    check_exits = (db.session.query(Friends).
                   filter(
                            or_(
                                and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                                and_(Friends.user_id == friend_id, Friends.friend_id == user_id)
                            )
                        ).
                   first())

    create_at = get_current_time()
    if check_exits:
        if check_exits.is_accept != -1:
            return my_json(ERROR_CAN_NOT_ADD_FRIEND)

        check_exits.is_accept = 0
        check_exits.create_at = create_at

        if check_exits.user_id != user_id:
            check_exits.user_id = user_id
            check_exits.friend_id = friend_id

        db.session.commit()
        notification_for_add_friend(current_user, friend_id, check_exits, create_at)

        return my_json("add friend id notification")

    try:
        is_accept = 0
        new_friend = Friends(user_id, friend_id, is_accept, create_at)

        db.session.add(new_friend)
        db.session.commit()

        notification_for_add_friend(current_user, friend_id, new_friend, create_at)

        return my_json("add friend id notification")
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def accept_service(friend_id, current_user):
    user_id = current_user.id

    if user_id == friend_id:
        return my_json(ERROR_CAN_NOT_ADD_YOURSELF)

    check_exits = (db.session.query(Friends).
                   filter(
                            or_(
                                and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                                and_(Friends.user_id == friend_id, Friends.friend_id == user_id)
                                ),
                            Friends.is_accept == 0
                          ).
                   first())

    if not check_exits:
        return my_json(ERROR_FRIEND_NOT_FOUND)

    try:
        check_exits.is_accept = 1

        user_create = db.session.query(Users).filter(Users.id == friend_id).first()
        user_create = user_schema.dump(user_create)

        room_id = create_room(current_user.username, current_user, user_create)

        if room_id is None:
            return my_json(ERROR_CAN_NOT_CREATE_ROOM)
        else:
            check_exits.id_room_chat = f"{room_id}"
            db.session.commit()

            notification_for_accept_friend(current_user, friend_id)

            return my_json({"room_id": str(room_id)})
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def unfriend_service(friend_id, current_user):
    user_id = current_user.id
    friend_id = friend_id

    friend = (db.session.query(Friends).
              filter(or_(
                      and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                      and_(Friends.user_id == friend_id, Friends.friend_id == user_id))
                     ).
              first())
    if not friend:
        return my_json(ERROR_FRIEND_NOT_FOUND)

    try:
        friend.is_accept = -1

        db.session.commit()
        return my_json("delete friend success")
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def return_result_friend(friends, user_id, cur_page, max_page):

    if friends:
        data_rs = []
        for result in friends:
            if result[0].user_id == user_id:
                user_id_rs = result[0].user_id
                friend_id_rs = result[0].friend_id
                username_rs = result[2].username
                avatar_rs = result[2].avatar
            else:
                user_id_rs = result[0].friend_id
                friend_id_rs = result[0].user_id
                username_rs = result[1].username
                avatar_rs = result[1].avatar

            data = {
                "user_id": user_id_rs,
                "friend_id": friend_id_rs,
                "name": username_rs,
                "avatar": avatar_rs
            }
            data_rs.append(data)

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(ERROR_FRIEND_NOT_FOUND)


def get_friend_by_id_service(page_num, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    if not page_num:
        return my_json(ERROR_PAGE_NUM_NULL)

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(
                        or_(Friends.user_id == user_id, Friends.friend_id == user_id),
                        Friends.is_accept == 1
                     ).
               order_by(Friends.create_at.desc()).
               paginate(page=page_num, per_page=PER_PAGE_LIST_FRIEND, error_out=False))

    cur_page = friends.page
    max_page = math.ceil(friends.total / PER_PAGE_LIST_FRIEND)

    return return_result_friend(friends, user_id, cur_page, max_page)


def get_invite_by_id_service(page_num, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    if not page_num:
        return my_json(ERROR_PAGE_NUM_NULL)

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(
                        Friends.friend_id == user_id,
                        Friends.is_accept == 0
                     ).
               order_by(Friends.create_at.desc()).
               paginate(page=page_num, per_page=PER_PAGE_LIST_FRIEND, error_out=False))

    cur_page = friends.page
    max_page = math.ceil(friends.total / PER_PAGE_LIST_FRIEND)

    return return_result_friend(friends, user_id, cur_page, max_page)


def get_room_chat_service(current_user, friend_id):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    if user_id == friend_id:
        return my_json(ERROR_CAN_NOT_ADD_YOURSELF)

    check_exits = (db.session.query(Friends).
                   filter(
                            or_(
                                and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                                and_(Friends.user_id == friend_id, Friends.friend_id == user_id)
                            ),
                            Friends.is_accept == 1
                        ).first())

    if not check_exits:
        return my_json(ERROR_FRIEND_NOT_FOUND)

    return my_json({'room_id': check_exits.id_room_chat})


def search_invite_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.json
    check_data = data and ('page' in data) and ('username' in data)

    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    page_num = data['page']
    username_search = data['username']
    if not page_num:
        return my_json(ERROR_PAGE_NUM_NULL)

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(
                        Friends.friend_id == user_id,
                        Friends.is_accept == 0,
                        user_alias.username.ilike(f'%{username_search}%')
                     ).
               order_by(Friends.create_at.desc()).
               paginate(page=page_num, per_page=PER_PAGE_LIST_FRIEND, error_out=False))

    cur_page = friends.page
    max_page = math.ceil(friends.total / PER_PAGE_LIST_FRIEND)

    return return_result_friend(friends, user_id, cur_page, max_page)


def search_friend_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.json
    check_data = data and ('page' in data) and ('username' in data)

    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    page_num = data['page']
    username_search = data['username'].lower()
    if not page_num:
        return my_json(ERROR_PAGE_NUM_NULL)

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(
                        or_(
                            and_(Friends.user_id == user_id, friend_alias.username.ilike(f'%{username_search}%')),
                            and_(Friends.friend_id == user_id, user_alias.username.ilike(f'%{username_search}%'))
                        ),
                        Friends.is_accept == 1
                     ).
               order_by(Friends.create_at.desc()).
               paginate(page=page_num, per_page=PER_PAGE_LIST_FRIEND, error_out=False))

    cur_page = friends.page
    max_page = math.ceil(friends.total / PER_PAGE_LIST_FRIEND)

    return return_result_friend(friends, user_id, cur_page, max_page)
