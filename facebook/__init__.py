from flask import Flask, jsonify
from .users.controller import users
from .friends.controller import friends
from .posts.controller import posts
from .extension import db, ma, jwt
from .model import Users, Friends, Posts, Comments, Likes, TokenBlocklist
import os
from datetime import timedelta


TIME_EXPIRES_ACCESS_TOKEN = 5
TIME_EXPIRES_REFRESH_TOKEN = 30


def create_db(app):
    if not os.path.exists("/instance/facebook.db"):
        with app.app_context():
            db.create_all()
        print("Create DB!!!")


def jwt_handel():
    # additional claims
    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        if not identity == "admin@gmail.com":
            return {"is_staff": True}
        return {"is_staff": False}

    # load user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]
        return Users.query.filter_by(email=identity).one_or_none()

    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_data):
        type_token = jwt_data['type']
        jti = jwt_data['jti']

        if type_token == 'refresh' and jti:
            token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
            return token is not None


def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    db.init_app(app)

    ma.init_app(app)
    create_db(app)
    app.register_blueprint(users)
    app.register_blueprint(friends)
    app.register_blueprint(posts)

    # Set up the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=TIME_EXPIRES_ACCESS_TOKEN)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=TIME_EXPIRES_REFRESH_TOKEN)
    print("Set up jwt")
    jwt.init_app(app)

    jwt_handel()

    return app
