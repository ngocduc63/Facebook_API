from pymongo import MongoClient, DESCENDING
from ..extension import get_current_time
from ..config import NOTIFICATION_FETCH_LIMIT, CONNECT_MONGO_PRODUCT, CONNECT_MONGO_DEV

client = MongoClient(CONNECT_MONGO_PRODUCT)

notification_db = client.get_database("NotificationDB")
notifications = notification_db.get_collection("notifications")


# type 1: notification for add friend
# type 2: notification for accept friend
# type 3: notification for like
# type 4: notification for comment


def add_notification_collection(user_id, data, type_notification):

    if type_notification == 1:
        data = {
            'user_id': data['created_by']['id']
        }
    elif type_notification == 2:
        data = {
            'user_id': data['id_friend']
        }
    elif type_notification == 3:
        data = {
            'user_id': data['post_id'],
            'category_react': data['category_react'],
            'post_id': data['post_id'],
        }
    elif type_notification == 4:
        data = {
            'user_id': data['user_id'],
            'post_id': data['post_id'],
        }

    notifications.insert_one({
        'for_user': user_id,
        'create_at': get_current_time(),
        'type': type_notification,
        'data': data
    })


def get_notifications_collection(user_id, page):
    offset = page * NOTIFICATION_FETCH_LIMIT
    result = list(
        notifications.find({'for_user': user_id}, {'_id': 0}).sort('_id', DESCENDING)
        .limit(NOTIFICATION_FETCH_LIMIT).skip(offset))

    total_notification = notifications.count_documents({'for_user': user_id})
    total_page = total_notification // NOTIFICATION_FETCH_LIMIT
    if total_notification % NOTIFICATION_FETCH_LIMIT != 0:
        total_page += 1

    return result, total_page

