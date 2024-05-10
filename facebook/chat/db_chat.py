from pymongo import MongoClient, DESCENDING
from ..extension import get_current_time
from bson import ObjectId
from ..config import MESSAGE_FETCH_LIMIT, LIST_ROOM_CHAT_FETCH_LIMIT

client = MongoClient("mongodb+srv://test:123@facebook.7yqdc0f.mongodb.net/?retryWrites=true&w=majority&appName=facebook")

chat_db = client.get_database("ChatDB")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")
messages_collection = chat_db.get_collection("messages")


def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': get_current_time()}).inserted_id
    # add_room_member(room_id, room_name, created_by, created_by)
    return room_id


def add_room_member(room_id, room_name, user_added, current_user):
    room_members_collection.insert_one(
        {
            '_id': {
                    'room_id': ObjectId(room_id),
            },
            'users': {
                    'username_key': {
                        'user_id': user_added['id'],
                        'username': user_added['username'],
                        'avatar': user_added['avatar'],
                    },
                    'username_friend': {
                        'user_id': current_user.id,
                        'username': current_user.username,
                        'avatar': current_user.avatar,
                    },
            },
            'room_name': room_name,
            'added_by': user_added['id'],
            'last_mess': {
                'sender': 0,
                'text': ''
            },
            'added_at': get_current_time()
        })


def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})


def get_room(room_id):
    return rooms_collection.find_one({'_id': ObjectId(room_id)})


def get_room_collection(room_id):
    return room_members_collection.find_one({'_id.room_id': ObjectId(room_id)})


def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': get_current_time()} for username in usernames])


def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_id, page=0):
    offset = page * LIST_ROOM_CHAT_FETCH_LIMIT

    list_room = list(room_members_collection.find({'_id.room_id': ObjectId(room_id)})
                     .sort('last_mess.created_at', DESCENDING)
                     .limit(LIST_ROOM_CHAT_FETCH_LIMIT).skip(offset)
                     )
    total_messages = room_members_collection.count_documents({'_id.room_id': ObjectId(room_id)})
    total_page = total_messages // LIST_ROOM_CHAT_FETCH_LIMIT
    if total_messages % LIST_ROOM_CHAT_FETCH_LIMIT != 0:
        total_page += 1

    return list_room, total_page


def update_avatar_in_room(username, avatar):
    query = {
        '$or': [
            {'users.username_key.user_id': username},
            {'users.username_friend.user_id': username}
        ]
    }
    list_room = list(room_members_collection.find(query))

    for room in list_room:
        if room['users']['username_key']['user_id'] == username:
            room_members_collection.update_one(
                {'_id': room['_id']},
                {'$set': {'users.username_key.avatar': avatar}}
            )
        else:
            room_members_collection.update_one(
                {'_id': room['_id']},
                {'$set': {'users.username_friend.avatar': avatar}}
            )


def update_username_in_room(username, name):
    query = {
        '$or': [
            {'users.username_key.user_id': username},
            {'users.username_friend.user_id': username}
        ]
    }
    list_room = list(room_members_collection.find(query))

    for room in list_room:
        if room['users']['username_key']['user_id'] == username:
            room_members_collection.update_one(
                {'_id': room['_id']},
                {'$set': {'users.username_key.username': name}}
            )
        else:
            room_members_collection.update_one(
                {'_id': room['_id']},
                {'$set': {'users.username_friend.username': name}}
            )


def get_rooms_for_user(username, page):
    offset = page * LIST_ROOM_CHAT_FETCH_LIMIT

    query = {
        '$or': [
            {'users.username_key.user_id': username},
            {'users.username_friend.user_id': username}
        ]
    }
    list_room = list(room_members_collection.find(query)
                     .sort('last_mess.created_at', DESCENDING)
                     .limit(LIST_ROOM_CHAT_FETCH_LIMIT).skip(offset)
                     )

    total_messages = room_members_collection.count_documents(query)
    total_page = total_messages // LIST_ROOM_CHAT_FETCH_LIMIT
    if total_messages % LIST_ROOM_CHAT_FETCH_LIMIT != 0:
        total_page += 1

    return list_room, total_page


def is_room_member(room_id, username):
    query = {
        '$or': [
            {'users.username_key.user_id': username},
            {'users.username_friend.user_id': username}
        ],
        '_id.room_id': ObjectId(room_id)
    }
    return room_members_collection.count_documents(query)


def save_message(data):
    (messages_collection.
        insert_one(
                    {
                        'room_id': data['room_id'],
                        'text': data['text'],
                        'sender': data['sender'],
                        'created_at': data['created_at']
                     }
                   )
     )

    data_room = get_room_collection(data['room_id'])
    watched = 0
    if data_room['last_mess']['sender'] != data['sender']:
        watched = 1

    room_members_collection.update_one({'_id.room_id': ObjectId(data['room_id'])},
                                       {'$set': {
                                           'last_mess': {
                                               'text': data['text'],
                                               'sender': data['sender'],
                                               'created_at': data['created_at'],
                                               'watched': watched,
                                           }}})


def get_messages(room_id, user_id, page=0):
    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(
        messages_collection.find({'room_id': room_id}, {'_id': 0}).sort('_id', DESCENDING)
        .limit(MESSAGE_FETCH_LIMIT).skip(offset))

    total_messages = messages_collection.count_documents({'room_id': room_id})
    total_page = total_messages // MESSAGE_FETCH_LIMIT
    if total_messages % MESSAGE_FETCH_LIMIT != 0:
        total_page += 1

    # update user watched
    data_room = get_room_collection(room_id)
    if user_id != int(data_room['last_mess']['sender']):
        room_members_collection.update_one({'_id.room_id': ObjectId(room_id)},
                                           {'$set': {'last_mess.watched': 1}})

    return messages, total_page
