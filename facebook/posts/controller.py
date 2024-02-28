from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, current_user
from flask import jsonify

posts = Blueprint("posts", __name__)


@posts.route("/post-management/post/get-new-feed/<int:page>")
@jwt_required()
def get_all_user(page):
    return jsonify({"mess": f"new feed page:{page}"})
