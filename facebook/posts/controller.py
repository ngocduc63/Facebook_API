from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user
from .services import get_new_feed_service, create_post_service

posts = Blueprint("posts", __name__)


@posts.route("/post-management/post/get-new-feed/<int:page>", methods=["GET"])
@jwt_required()
def get_new_feed(page):
    return get_new_feed_service(page, current_user)


@posts.route("/post-management/post/create", methods=["POST"])
@jwt_required()
def create_post():
    return create_post_service(current_user)
