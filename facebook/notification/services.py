from .db_notification import save_notification_add_friend, get_notification_add_friend
from ..extension import my_json, obj_success_paginate
from ..config_error_code import ERROR_CHECK_TOKEN


def create_notification_add_friend_service(data):
    if (data and ('description' in data) and ('created_by' in data)
            and ('for_user_id' in data) and ('create_at' in data) and ('id_friend' in data)):

        add_friend_id = save_notification_add_friend(data)
        return add_friend_id

    else:
        return None


def get_notification_add_friend_service(current_user, page):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data_rs = get_notification_add_friend(user_id, page)

    return my_json(obj_success_paginate(data_rs, page, -1))
