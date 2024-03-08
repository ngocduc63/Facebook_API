from facebook.extension import db
from facebook.facebook_ma import PostSchema, UserSchema, LikeSchema, CommentSchema
from facebook.model import Posts, Likes, Comments
from ..extension import (my_json, obj_success_paginate, get_current_time, change_name_file, get_path_upload,
                         allowed_file)
from ..config import PER_PAGE_POST
from flask import request, json
from werkzeug.utils import secure_filename

UPLOAD_POST_FOLDER = "upload/post"

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
user_schema = UserSchema()
like_schema = LikeSchema()
comment_schema = CommentSchema()


def get_new_feed_service(page, current_user):
    return my_json(f"new feed: page {page}")


def create_post_service(current_user):
    try:
        user_id = user_schema.dump(current_user)['id']
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
        user_id = user_schema.dump(current_user)['id']
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
        user_id = user_schema.dump(current_user)['id']
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
        user_id = user_schema.dump(current_user)['id']
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
                db.session.add(new_like)
                db.session.commit()

                data_like = like_schema.dump(new_like)
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
        user_id = user_schema.dump(current_user)['id']
    except Exception as e:
        print(e)
        return my_json(error_code=4, mess="token not match user id")

    if id_post and user_id:
        like = db.session.query(Likes).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()

        if not like:
            return my_json(error_code=3, mess="not found like post")

        try:
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
        user_id = user_schema.dump(current_user)['id']
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
                db.session.add(new_comment)
                db.session.commit()

                data_like = like_schema.dump(new_comment)
                return my_json(data_like)
            except IndentationError:
                db.session.rollback()
                return my_json(error_code=1, mess="error in DB")
        else:
            return my_json(error_code=2, mess="error data request")
    else:
        return my_json(error_code=3, mess="error data request")


def user_delete_comment_post_service(id_post, current_user):
    try:
        user_id = user_schema.dump(current_user)['id']
    except Exception as e:
        print(e)
        return my_json(error_code=4, mess="token not match user id")

    if id_post and user_id:
        comment = db.session.query(Comments).filter(Likes.user_id == user_id, Likes.post_id == id_post).first()

        if not comment:
            return my_json(error_code=3, mess="not found comment post")

        try:
            comment.isDelete = 1

            db.session.commit()
            return my_json("delete comment success")
        except IndentationError:
            db.session.rollback()
            return my_json(error_code=1, mess="error in DB")
    else:
        return my_json(error_code=2, mess="error data request")