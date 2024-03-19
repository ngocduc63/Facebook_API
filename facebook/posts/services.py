from facebook.extension import db
from facebook.facebook_ma import PostSchema, LikeSchema, CommentSchema
from facebook.model import Posts, Likes, Comments, Users
from ..extension import (my_json, obj_success_paginate, get_current_time, change_name_file, get_path_upload,
                         allowed_file, get_path_local)
from ..config import PER_PAGE_POST, PER_PAGE_LIKE_POST, PER_PAGE_COMMENT_POST
from flask import request, json, send_from_directory
from werkzeug.utils import secure_filename
import math
from ..socketio_instance import socketio

UPLOAD_POST_FOLDER = "upload/post"

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
like_schema = LikeSchema()
comment_schema = CommentSchema()


def get_new_feed_service(page_num, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=1, mess="token not match user id")

    posts = (db.session.
             query(Posts, Users)
             .outerjoin(Users, Users.id == Posts.user_id)
             .filter(Posts.user_id == user_id)
             .order_by(Posts.create_at.desc())
             .paginate(page=page_num, per_page=PER_PAGE_POST, error_out=False)
             )

    cur_page = posts.page
    max_page = math.ceil(posts.total / PER_PAGE_POST)

    if posts:
        data_rs = []
        for result in posts:
            data = {
                "id": result[0].id,
                "user": {
                    "id": result[1].id,
                    "username": result[1].username,
                    "avatar": result[1].avatar
                },
                "title": result[0].title,
                "image": result[0].image,
                "create_at": result[0].create_at,
                "num_like": result[0].count_like,
                "num_comment": result[0].count_comment
            }
            data_rs.append(data)

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(error_code=1, mess="not found post")


def get_users_like_post_service():
    data = request.json

    check_data = data and ('post_id' in data) and ('page' in data)

    if check_data:
        post_id = data['post_id']
        page_num = data['page']

        likes = (db.session.query(Likes, Users)
                 .outerjoin(Users, Users.id == Likes.user_id)
                 .filter(Likes.post_id == post_id)
                 .group_by(Likes.id)
                 .order_by(Likes.create_at.desc())
                 .paginate(page=page_num, per_page=PER_PAGE_LIKE_POST, error_out=False)
                 )

        cur_page = likes.page
        max_page = math.ceil(likes.total / PER_PAGE_LIKE_POST)

        if likes:
            data_rs = []
            for result in likes:
                data = {
                    "id": result[0].id,
                    "user": {
                        "id": result[1].id,
                        "username": result[1].username,
                        "avatar": result[1].avatar
                    },
                    "create_at": result[0].create_at,
                }
                data_rs.append(data)

            return my_json(obj_success_paginate(data_rs, cur_page, max_page))
        else:
            return my_json(error_code=2, mess="not found like")

    else:
        return my_json(error_code=1, mess="not found data request")


def get_users_comment_post_service():
    data = request.json

    check_data = data and ('post_id' in data) and ('page' in data)

    if check_data:
        post_id = data['post_id']
        page_num = data['page']

        comments = (db.session.query(Comments, Users)
                    .outerjoin(Users, Users.id == Comments.user_id)
                    .filter(Comments.post_id == post_id)
                    .group_by(Comments.id)
                    .order_by(Comments.create_at.desc())
                    .paginate(page=page_num, per_page=PER_PAGE_COMMENT_POST, error_out=False)
                    )

        cur_page = comments.page
        max_page = math.ceil(comments.total / PER_PAGE_COMMENT_POST)

        if comments:
            data_rs = []
            for result in comments:
                data = {
                    "id": result[0].id,
                    "user": {
                        "id": result[1].id,
                        "username": result[1].username,
                        "avatar": result[1].avatar
                    },
                    "content": result[0].content,
                    "create_at": result[0].create_at
                }
                data_rs.append(data)

            return my_json(obj_success_paginate(data_rs, cur_page, max_page))
        else:
            return my_json(error_code=2, mess="not found comment")

    else:
        return my_json(error_code=1, mess="not found data request")


def create_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=4, mess="token not match user id")

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
        return my_json(error_code=3, mess="error validate data")


def update_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=4, mess="token not match user id")

    data = json.loads(request.form['data'])

    check_data = data and ('title' in data) and ('status' in data) and ('id' in data)

    if check_data and user_id:
        id_post = data["id"]
        title_new = data["title"]
        status_new = data['status']
        image_str_new = ""

        data_image = request.files
        if data_image:
            file = data_image['image']
            if file and allowed_file(file.filename):
                try:
                    filename_full = secure_filename(file.filename)
                    filename = change_name_file(filename_full, user_id)
                    file.save(get_path_upload(UPLOAD_POST_FOLDER, filename))
                    image_str_new = filename
                except Exception as e:
                    print(e)
                    return my_json(error_code=2, mess="error upload file")

        try:
            post = db.session.query(Posts).filter(Posts.id == id_post).first()
            post.title = title_new
            post.status = status_new
            post.image = image_str_new

            post_data = post_schema.dump(post)
            db.session.commit()
            return my_json(post_data)
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=3, mess="error validate data")


def delete_post_service(id_post, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=3, mess="token not match user id")

    if id_post and user_id:
        try:
            post = db.session.query(Posts).filter(Posts.id == id_post).first()
            post.isDelete = 1

            post_data = post_schema.dump(post)
            db.session.commit()
            return my_json(post_data)
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=2, mess="error validate data")


def user_like_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=6, mess="token not match user id")

    data = request.json
    check_data = data and ('id_post' in data) and ('category' in data)

    if check_data:
        id_post = data['id_post']
        category = data['category']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(error_code=4, mess="not found post")

        like = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()
        if like:
            return my_json(error_code=5, mess="pos was liked")

        if id_post and user_id:
            try:
                create_at = get_current_time()
                new_like = Likes(user_id, id_post, category, create_at)
                post.count_like = post.count_like + 1
                db.session.add(new_like)
                db.session.commit()

                data_like = like_schema.dump(new_like)
                data_notification = {
                    "mess": f"{current_user.username} đã thả cảm xúc bài viết của bạn",
                    "user_name": current_user.username,
                    "avatar": current_user.avatar,
                    "category_react": category,
                    "num_like": post.count_like,
                    "create_at": create_at
                }
                socketio.emit('receive_notification_post', data_notification, room=f'post_{data_like['post_id']}')

                return my_json(data_like)
            except IndentationError:
                db.session.rollback()
                return my_json(error_code=1, mess="error in DB")
        else:
            return my_json(error_code=2, mess="error data request")
    else:
        return my_json(error_code=3, mess="error data request")


def user_unlike_post_service(id_post, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=5, mess="token not match user id")

    if id_post and user_id:

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(error_code=4, mess="not found post")

        like = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()
        if not like:
            return my_json(error_code=3, mess="not found like post")

        try:
            post.count_like = post.count_like - 1
            db.session.delete(like)
            db.session.commit()
            return my_json("unlike success")
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=2, mess="error data request")


def user_comment_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=5, mess="token not match user id")

    data = request.json
    check_data = data and ('id_post' in data) and ('content' in data)

    if check_data:
        id_post = data['id_post']
        content = data['content']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(error_code=4, mess="not found post")

        if id_post and user_id:
            try:
                create_at = get_current_time()
                new_comment = Comments(user_id, id_post, content, 0, create_at)
                post.count_comment = post.count_comment + 1
                db.session.add(new_comment)
                db.session.commit()

                data_comment = comment_schema.dump(new_comment)
                data_notification = {
                    "mess": f"{current_user.username} đã bình luận bài viết của bạn",
                    "avatar": current_user.avatar,
                    "user_name": current_user.username,
                    "create_at": create_at
                }
                socketio.emit('receive_notification_post', data_notification, room=f'post_{data_comment['post_id']}')

                return my_json(data_comment)
            except IndentationError:
                db.session.rollback()
                return my_json(error_code=1, mess="error in DB")
        else:
            return my_json(error_code=2, mess="error data request")
    else:
        return my_json(error_code=3, mess="error data request")


def user_delete_comment_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(error_code=7, mess="token not match user id")

    data = request.json
    check_data = data and ('id_post' in data) and ('id_comment' in data)

    if check_data:
        id_post = data['id_post']
        id_comment = data['id_comment']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(error_code=6, mess="not found post")

        comment = db.session.query(Comments).filter(Comments.id == id_comment).first()
        if not comment:
            return my_json(error_code=5, mess="not found comment post")

        if comment.isDeleted == 1:
            return my_json(error_code=4, mess="comment was deleted")

        if post.user_id != user_id:
            return my_json(error_code=3, mess="user can't delete comment")

        try:
            comment.isDeleted = 1
            post.count_comment = post.count_comment - 1

            db.session.commit()
            return my_json("delete comment success")
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=2, mess="error data request")


def image_post_service(filename):
    return send_from_directory(get_path_local(UPLOAD_POST_FOLDER), filename)
