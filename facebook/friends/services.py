import math
from facebook.extension import db
from facebook.facebook_ma import FriendSchema, UserSchema
from facebook.model import Friends, Users
from flask import request
import time
from ..extension import my_json, obj_success_paginate
from ..config import PER_PAGE_LIST_FRIEND
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

friend_schema = FriendSchema()
user_schema = UserSchema()
friends_schema = FriendSchema(many=True)
user_alias = aliased(Users)
friend_alias = aliased(Users)


def add_friend_service(friend_id, current_user):
    user_id = user_schema.dump(current_user)['id']
    friend_id = friend_id

    if user_id == friend_id:
        return my_json(error_code=2, mess="Can not add yourself")

    check_exits = (db.session.query(Friends).
                   filter(or_(
                              and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                              and_(Friends.user_id == friend_id, Friends.friend_id == user_id))
                          ).
                   first())

    if check_exits:
        return my_json(error_code=3, mess="Can not add because They were friend")

    create_at = int(time.time())
    try:
        new_friend = Friends(user_id, friend_id, create_at)

        db.session.add(new_friend)
        db.session.commit()
        return my_json("add friend success")
    except IndentationError:
        db.session.rollback()
        return my_json(error_code=1, mess="error query database")


def unfriend_service(friend_id, current_user):
    user_id = user_schema.dump(current_user)['id']
    friend_id = friend_id

    friend = (db.session.query(Friends).
              filter(or_(
                      and_(Friends.user_id == user_id, Friends.friend_id == friend_id),
                      and_(Friends.user_id == friend_id, Friends.friend_id == user_id))
                     ).
              first())
    if not friend:
        return my_json(error_code=3, mess="not found friend")

    try:
        db.session.delete(friend)
        db.session.commit()
        return my_json("delete friend success")
    except IndentationError:
        db.session.rollback()
        return my_json(error_code=1, mess="error query database")


def get_friend_by_id_service(user_id):
    page_num = request.json["page"]

    if not page_num:
        return my_json(error_code=2, mess="not found page number")

    friends = (db.session.query(Friends, user_alias, friend_alias).
               join(user_alias, Friends.user_id == user_alias.id).
               join(friend_alias, Friends.friend_id == friend_alias.id).
               filter(or_(Friends.user_id == user_id, Friends.friend_id == user_id)).
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

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(error_code=1, mess="not found friend")
