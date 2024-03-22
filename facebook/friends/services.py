import math
from facebook.extension import db
from facebook.facebook_ma import FriendSchema
from facebook.model import Friends, Users
from flask import request
from ..extension import my_json, obj_success_paginate, get_current_time, obj_success
from ..config import PER_PAGE_LIST_FRIEND
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased
from ..chat.controller import create_room
from ..config_error_code import (ERROR_SAVE_DB,  ERROR_FRIEND_NOT_FOUND, ERROR_CAN_NOT_ADD_FRIEND,
                                 ERROR_CAN_NOT_ADD_YOURSELF, ERROR_CAN_NOT_CREATE_ROOM, ERROR_PAGE_NUM_NULL)

friend_schema = FriendSchema()
friends_schema = FriendSchema(many=True)
user_alias = aliased(Users)
friend_alias = aliased(Users)


def add_friend_service(friend_id, current_user):
    user_id = current_user.id
    friend_id = friend_id

    if user_id == friend_id:
        return my_json(ERROR_CAN_NOT_ADD_YOURSELF)

    check_friend = db.session.query(Users).filter(Users.id == friend_id).first()

    if not check_friend:
        return my_json(ERROR_FRIEND_NOT_FOUND)

    check_exits = (db.session.query(Friends).
                   filter(
                            or_(
                                and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                                and_(Friends.user_id == friend_id, Friends.friend_id == user_id)
                            )
                        ).
                   first())

    if check_exits:
        return my_json(ERROR_CAN_NOT_ADD_FRIEND)

    create_at = get_current_time()
    try:
        is_accept = 0
        new_friend = Friends(user_id, friend_id, is_accept, create_at)

        db.session.add(new_friend)
        db.session.commit()

        return my_json("add friend success")
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def accept_service(user_id, current_user):
    friend_id = current_user.id

    if user_id == friend_id:
        return my_json(ERROR_CAN_NOT_ADD_YOURSELF)

    check_exits = (db.session.query(Friends).
                   filter(
                            Friends.user_id == user_id, Friends.friend_id == friend_id,
                            Friends.is_accept == 0
                          ).
                   first())

    if not check_exits:
        return my_json(ERROR_FRIEND_NOT_FOUND)

    try:
        check_exits.is_accept = 1

        room_id = create_room(current_user.username, user_id, friend_id)
        if room_id == "":
            return my_json(ERROR_CAN_NOT_CREATE_ROOM)
        else:
            db.session.commit()
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
        db.session.delete(friend)
        db.session.commit()
        return my_json("delete friend success")
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def get_friend_by_id_service(user_id):
    page_num = request.json["page"]

    if not page_num:
        return my_json(ERROR_PAGE_NUM_NULL)

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(
                        or_(Friends.user_id == user_id, Friends.friend_id == user_id),
                        Friends.is_accept == 1
                     ).
               paginate(page=page_num, per_page=PER_PAGE_LIST_FRIEND, error_out=False))

    cur_page = friends.page
    max_page = math.ceil(friends.total / PER_PAGE_LIST_FRIEND)

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

        data_rs.sort(key=lambda x: x["name"])

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(ERROR_FRIEND_NOT_FOUND)
