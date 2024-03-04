from facebook.extension import db
from facebook.facebook_ma import PostSchema, UserSchema
from facebook.model import Posts
from ..extension import (my_json, obj_success_paginate, get_current_time, change_name_file, get_path_upload,
                         allowed_file)
from ..config import PER_PAGE_POST
from flask import request, json
from werkzeug.utils import secure_filename

UPLOAD_POST_FOLDER = "upload/post"

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
user_schema = UserSchema()


def get_new_feed_service(page, current_user):
    return my_json(f"new feed: page {page}")


def create_post_service(current_user):
    user_id = user_schema.dump(current_user)["id"]
    data = json.loads(request.form['data'])

    check_data = data and ('title' in data) and ('status' in data)

    if check_data and user_id:

        title = data["title"]
        status = data['status']
        image_str = ""
        is_delete = 0
        create_at = get_current_time()

        data_image = request.files
        if data_image:
            file = data_image['image']
            if file and allowed_file(file.filename):
                try:
                    filename_full = secure_filename(file.filename)
                    filename = change_name_file(filename_full, user_id)
                    file.save(get_path_upload(UPLOAD_POST_FOLDER, filename))
                    image_str = filename
                except Exception as e:
                    print(e)
                    return my_json(error_code=2, mess="error upload file")

        try:
            new_post = Posts(title, image_str, user_id, status, is_delete, create_at)

            db.session.add(new_post)
            db.session.commit()
            return my_json(post_schema.dump(new_post))
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=2, mess="error validate data")

