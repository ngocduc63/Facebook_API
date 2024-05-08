from facebook.extension import db
from facebook.facebook_ma import PostSchema, LikeSchema, CommentSchema
from facebook.model import Posts, Likes, Comments, Users, Friends
from ..extension import (my_json, obj_success_paginate, get_current_time, change_name_file, get_path_upload,
                         allowed_file, get_path_local)
from ..config import PER_PAGE_POST, PER_PAGE_LIKE_POST, PER_PAGE_COMMENT_POST
from flask import request, json, send_from_directory
from werkzeug.utils import secure_filename
import math
from ..socketio_instance import socketio
from ..config_error_code import (ERROR_DATA_NOT_MATCH, ERROR_FILE_NULL, ERROR_UPLOAD_FILE, ERROR_CHECK_TOKEN,
                                 ERROR_SAVE_DB, ERROR_USER_HAVE_NOT_ROLE, ERROR_POST_NOT_FOUND, ERROR_LIKE_NOT_FOUND,
                                 ERROR_COMMENT_NOT_FOUND, ERROR_LIKE_IN_POST_EXIST)
from sqlalchemy import and_, or_

UPLOAD_POST_FOLDER = "upload/post"

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
like_schema = LikeSchema()
comment_schema = CommentSchema()


def check_user_like_post(user_id, post_id):
    data = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == post_id).first()
    return 1 if data else 0


def get_posts_by_user_service(current_user):
    data = request.json

    check_data = data and ('user_id' in data) and ('page' in data)

    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    user_id = data['user_id']
    page_num = data['page']
    posts = (db.session.query(Posts, Users).
             outerjoin(Users, Users.id == Posts.user_id)
             .filter(Posts.user_id == user_id, Posts.isDeleted == 0)
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
                "category": result[0].category,
                "create_at": result[0].create_at,
                "num_like": result[0].count_like,
                "num_comment": result[0].count_comment,
                'liked': check_user_like_post(current_user.id, result[0].id)
            }
            data_rs.append(data)

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(ERROR_POST_NOT_FOUND)


def get_new_feed_service(page_num, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    friends = Friends.query.filter(or_(Friends.user_id == user_id, Friends.friend_id == user_id)).all()
    friend_ids = [friend.user_id if friend.user_id != user_id else friend.friend_id for friend in friends]
    posts = (db.session.query(Posts, Users).
             outerjoin(Users, Users.id == Posts.user_id)
             .filter(or_(Posts.user_id.in_(friend_ids), Posts.user_id == user_id), Posts.isDeleted == 0)
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
                "category": result[0].category,
                "create_at": result[0].create_at,
                "num_like": result[0].count_like,
                "num_comment": result[0].count_comment,
                'liked': check_user_like_post(user_id, result[0].id)
            }
            data_rs.append(data)

        return my_json(obj_success_paginate(data_rs, cur_page, max_page))
    else:
        return my_json(ERROR_POST_NOT_FOUND)


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
            return my_json(ERROR_LIKE_NOT_FOUND)

    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def get_users_comment_post_service():
    data = request.json

    check_data = data and ('post_id' in data) and ('page' in data)

    if check_data:
        post_id = data['post_id']
        page_num = data['page']

        comments = (db.session.query(Comments, Users)
                    .outerjoin(Users, Users.id == Comments.user_id)
                    .filter(Comments.post_id == post_id, Comments.isDeleted != 1)
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
            return my_json(ERROR_COMMENT_NOT_FOUND)

    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def create_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

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
                    return my_json(ERROR_UPLOAD_FILE)
            else:
                return my_json(ERROR_FILE_NULL)

        try:
            new_post = Posts(title, image_str, user_id, status, is_delete, 0, create_at)

            db.session.add(new_post)
            db.session.commit()
            return my_json(post_schema.dump(new_post))
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def update_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = json.loads(request.form['data'])

    check_data = data and ('title' in data) and ('status' in data) and ('id' in data)

    if check_data and user_id:
        id_post = data["id"]
        title_new = data["title"]
        status_new = data['status']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()

        data_image = request.files

        if data_image:
            file = data_image['image']
            if file and allowed_file(file.filename):
                try:
                    filename_full = secure_filename(file.filename)
                    filename = change_name_file(filename_full, user_id)
                    file.save(get_path_upload(UPLOAD_POST_FOLDER, filename))
                    image_str_new = filename

                    post.title = title_new
                    post.status = status_new
                    post.image = image_str_new

                    post_data = post_schema.dump(post)
                    db.session.commit()
                    return my_json(post_data)
                except IndentationError:
                    db.session.rollback()
                    return my_json(ERROR_SAVE_DB)
                except Exception as e:
                    print(e)
                    return my_json(ERROR_UPLOAD_FILE)
            else:
                return my_json(ERROR_FILE_NULL)
        else:
            post.title = title_new
            post.status = status_new

            post_data = post_schema.dump(post)
            db.session.commit()
            return my_json(post_data)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def delete_post_service(id_post, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    if id_post and user_id:
        try:
            post = db.session.query(Posts).filter(Posts.id == id_post).first()
            post.isDeleted = 1

            post_data = post_schema.dump(post)
            db.session.commit()
            return my_json(post_data)
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def user_like_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.json
    check_data = data and ('id_post' in data) and ('category' in data)

    if check_data:
        id_post = data['id_post']
        category = data['category']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(ERROR_POST_NOT_FOUND)

        like = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()
        if like:
            return my_json(ERROR_LIKE_IN_POST_EXIST)

        try:
            create_at = get_current_time()
            new_like = Likes(user_id, id_post, category, create_at)
            post.count_like = post.count_like + 1
            db.session.add(new_like)
            db.session.commit()

            data_like = like_schema.dump(new_like)
            data_notification = {
                "mess": "đã thả cảm xúc bài viết của bạn",
                "post_id": data_like['post_id'],
                "user_id": current_user.id,
                "user_name": current_user.username,
                "avatar": current_user.avatar,
                "category_react": category,
                "num_like": post.count_like,
                "create_post": post.user_id,
                "create_at": create_at
            }
            socketio.emit('notification_post', data_notification, room=f'post_{data_like["post_id"]}')

            return my_json(data_like)
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def user_unlike_post_service(id_post, current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    if id_post and user_id:

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(ERROR_POST_NOT_FOUND)

        like = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()
        if not like:
            return my_json(ERROR_LIKE_NOT_FOUND)

        try:
            post.count_like = post.count_like - 1
            db.session.delete(like)
            db.session.commit()

            data_notification = {
                "mess": "un_like",
                "post_id": post.id,
                "user_id": current_user.id,
                "num_like": post.count_like,
                "create_post": post.user_id,
            }
            socketio.emit('notification_post', data_notification, room=f'post_{post.id}')

            return my_json("unlike success")
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def user_comment_post_service(current_user):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    data = request.json
    check_data = data and ('id_post' in data) and ('content' in data)

    if check_data:
        id_post = data['id_post']
        content = data['content']

        post = db.session.query(Posts).filter(Posts.id == id_post).first()
        if not post:
            return my_json(ERROR_POST_NOT_FOUND)

        try:
            create_at = get_current_time()
            new_comment = Comments(user_id, id_post, content, 0, create_at)
            post.count_comment = post.count_comment + 1
            db.session.add(new_comment)
            db.session.commit()

            data_comment = comment_schema.dump(new_comment)
            data_notification = {
                "mess": "đã bình luận bài viết của bạn",
                "post_id": data_comment['post_id'],
                "user_id": current_user.id,
                "user_name": current_user.username,
                "avatar": current_user.avatar,
                "num_comment": post.count_comment,
                "create_post": post.user_id,
                "create_at": create_at
            }
            socketio.emit('notification_post', data_notification, room=f'post_{data_comment["post_id"]}')

            return my_json(data_comment)
        except IndentationError:
            db.session.rollback()
            return my_json(ERROR_SAVE_DB)
    else:
        return my_json(ERROR_DATA_NOT_MATCH)


def user_delete_comment_post_service(current_user, id_comment):
    try:
        user_id = current_user.id
    except Exception as e:
        print(e)
        return my_json(ERROR_CHECK_TOKEN)

    comment = db.session.query(Comments).filter(Comments.id == id_comment).first()
    if not comment:
        return my_json(ERROR_COMMENT_NOT_FOUND)

    comment_data = comment_schema.dump(comment)
    post = db.session.query(Posts).filter(Posts.id == comment_data['post_id']).first()
    if not post:
        return my_json(ERROR_POST_NOT_FOUND)

    post_data = post_schema.dump(post)

    if comment.isDeleted == 1:
        return my_json(ERROR_COMMENT_NOT_FOUND)

    if comment.user_id != user_id and user_id != post_data['user_id']:
        return my_json(ERROR_USER_HAVE_NOT_ROLE)

    try:
        comment.isDeleted = 1
        post.count_comment = post.count_comment - 1
        db.session.commit()

        data_notification = {
            "num_comment": post.count_comment,
        }
        socketio.emit('notification_post', data_notification, room=f'post_{post.id}')

        return my_json("delete comment success")
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def update_comment_service():
    data = request.json

    check_data = data and ('id_comment' in data) and ('content' in data)
    if not check_data:
        return my_json(ERROR_DATA_NOT_MATCH)

    id_comment = data['id_comment']
    content = data['content']

    comment = db.session.query(Comments).filter(Comments.id == id_comment, Comments.isDeleted != 1).first()

    if not comment:
        return my_json(ERROR_COMMENT_NOT_FOUND)

    try:
        comment.content = content
        db.session.commit()
        
        comment_data = comment_schema.dump(comment)
        return my_json(comment_data)
    except IndentationError:
        db.session.rollback()
        return my_json(ERROR_SAVE_DB)


def image_post_service(filename):
    return send_from_directory(get_path_local(UPLOAD_POST_FOLDER), filename)
