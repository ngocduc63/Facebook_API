from ..extension import my_json, obj_success_paginate
from ..config_error_code import ERROR_CHECK_TOKEN, ERROR_USER_NOT_FOUND
from .db_notification import get_notifications_collection
from facebook.facebook_ma import UserSchema
from facebook.model import Users

user_schema = UserSchema()


def get_notifications_for_user_service(current_user, page):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    datas, total_page = get_notifications_collection(user_id, page - 1)

    data_rs = []
    for data in datas:
        user = Users.query.get(data['data']['user_id'])
        if not user:
            return my_json(ERROR_USER_NOT_FOUND)

        user_data = user_schema.dump(user)
        user_rs = {
            'id': user_data['id'],
            'avatar': user_data['avatar'],
            'username': user_data['username'],
        }
        data.update({'user': user_rs})
        data_rs.append(data)

    return my_json(obj_success_paginate(data_rs, page, total_page))



