from library.extension import db
from library.facebook_ma import FriendSchema
from library.model import Friends
from flask import request, jsonify
import time

friend_schema = FriendSchema()
friends_schema = FriendSchema(many=True)


def add_friend_service():
    data = request.json
    check_data = (data and ('friend_id' in data) and ('user_id' in data))

    if check_data:

        user_id = data['user_id']
        friend_id = data['friend_id']

        create_at = int(time.time())
        try:
            new_friend = Friends(user_id, friend_id, create_at)

            db.session.add(new_friend)
            db.session.commit()
            return "Add friend success"
        except IndentationError:
            db.session.rollback()
            return "Can not add friend"

    else:
        return "Request error"

def get_friend_by_id_service(id):
    friend = Friends.query.get(id)

    if friend:
        return friend_schema.jsonify(friend)
    else:
        return "Not found friend"


def get_all_friend_service():
    friends = Friends.query.all()

    if friends:
        return friends_schema.jsonify(friends)
    else:
        return "Not found friend"
