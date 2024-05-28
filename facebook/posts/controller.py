from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import (get_new_feed_service, create_post_service, update_post_service, delete_post_service,
                       user_like_post_service, user_unlike_post_service, user_comment_post_service,
                       user_delete_comment_post_service, image_post_service, get_users_like_post_service,
                       get_users_comment_post_service, get_posts_by_user_service, update_comment_service,
                       get_post_by_id_service, create_post_share_service)
from flask_socketio import join_room, leave_room
from facebook.socketio_instance import socketio

posts = Blueprint("posts", __name__)


# api
@posts.route("/post-management/post/get-new-feed/<int:page>", methods=["GET"])
@jwt_required()
def get_new_feed(page):
    return get_new_feed_service(page, current_user)


@posts.route("/post-management/post/get-user-posts", methods=["post"])
@jwt_required()
def get_user_posts():
    return get_posts_by_user_service(current_user)


@posts.route("/post-management/post/<int:post_id>", methods=["get"])
@jwt_required()
def get_posts(post_id):
    return get_post_by_id_service(post_id, current_user)


@posts.route("/post-management/post/create", methods=["POST"])
@jwt_required()
def create_post():
    return create_post_service(current_user)


@posts.route("/post-management/post/share", methods=["POST"])
@jwt_required()
def share_post():
    return create_post_share_service(current_user)


@posts.route("/post-management/post/likes", methods=["POST"])
@jwt_required()
def get_users_like_post():
    return get_users_like_post_service()


@posts.route("/post-management/post/comments", methods=["POST"])
@jwt_required()
def get_users_comment_post():
    return get_users_comment_post_service()


@posts.route("/post-management/post/image/<string:filename>", methods=["GET"])
def get_image(filename):
    return image_post_service(filename)


@posts.route("/post-management/post/update", methods=["PUT"])
@jwt_required()
def update_post():
    return update_post_service(current_user)


@posts.route("/post-management/post/delete/<int:id_post>", methods=["DELETE"])
@jwt_required()
def delete_post(id_post):
    return delete_post_service(id_post, current_user)


@posts.route("/post-management/post/like", methods=["POST"])
@jwt_required()
def like_post():
    return user_like_post_service(current_user)


@posts.route("/post-management/post/unlike/<int:id_post>", methods=["DELETE"])
@jwt_required()
def unlike_post(id_post):
    return user_unlike_post_service(id_post, current_user)


@posts.route("/post-management/post/comment", methods=["POST"])
@jwt_required()
def comment_post():
    return user_comment_post_service(current_user)


@posts.route("/post-management/post/delete-comment/<int:id_comment>", methods=["DELETE"])
@jwt_required()
def delete_comment_post(id_comment):
    return user_delete_comment_post_service(current_user, id_comment)


@posts.route("/post-management/post/update-comment", methods=["PUT"])
@jwt_required()
def update_comment_post():
    return update_comment_service()


# socket
@socketio.on('join_notification_post')
def handle_join_post_notification_event(data):
    join_room(f'post_{data["post_id"]}')
    socketio.emit('join_notification_post', data, room=f'post_{data["post_id"]}')


@socketio.on('leave_notification_post')
def handle_leave_post_notification_event(data):
    leave_room(f'post_{data["post_id"]}')
    socketio.emit('join_notification_post', data, room=f'post_{data["post_id"]}')
