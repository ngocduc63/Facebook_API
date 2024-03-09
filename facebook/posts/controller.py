from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import (get_new_feed_service, create_post_service, update_post_service, delete_post_service,
                       user_like_post_service, user_unlike_post_service, user_comment_post_service,
                       user_delete_comment_post_service)


posts = Blueprint("posts", __name__)


@posts.route("/post-management/post/get-new-feed/<int:page>", methods=["GET"])
@jwt_required()
def get_new_feed(page):
    return get_new_feed_service(page, current_user)


@posts.route("/post-management/post/create", methods=["POST"])
@jwt_required()
def create_post():
    return create_post_service(current_user)


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


@posts.route("/post-management/post/delete-comment/<int:id_post>", methods=["DELETE"])
@jwt_required()
def delete_comment_post(id_post):
    return user_delete_comment_post_service(id_post, current_user)
