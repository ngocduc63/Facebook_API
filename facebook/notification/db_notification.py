from pymongo import MongoClient, DESCENDING
from ..config import ADD_FRIEND_FETCH_LIMIT

client = MongoClient("mongodb+srv://test:123@facebook.7yqdc0f.mongodb.net/?retryWrites=true&w=majority&appName=facebook")

notification_db = client.get_database("NotificationDB")
notification_info_collection = notification_db.get_collection("notification_info")
notification_friend_collection = notification_db.get_collection("notification_friend")
notification_post_collection = notification_db.get_collection("notification_post")

# category 1: notification for add friend
# category 2: notification for like, comment
# category 3: notification for post


def save_notification_add_friend(data):
    notification_id = notification_friend_collection.insert_one(data)
    return notification_id


def get_notification_add_friend(user_id, page_num=1):
    page = page_num - 1
    offset = page * ADD_FRIEND_FETCH_LIMIT
    data = list(notification_friend_collection.find({'for_user_id': user_id}, {'_id': 0})
                .sort('create_at', DESCENDING).limit(ADD_FRIEND_FETCH_LIMIT).skip(offset))
    return data
