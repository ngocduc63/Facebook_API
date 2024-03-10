from pymongo import MongoClient
from ..extension import get_current_time
from bson import ObjectId

client = MongoClient("mongodb+srv://test:123@facebook.7yqdc0f.mongodb.net/?retryWrites=true&w=majority&appName=facebook")

chat_db = client.get_database("ChatDB")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")


def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': get_current_time()}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id


def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': get_current_time(), 'is_room_admin': is_room_admin})
