from flask import Flask, redirect, Blueprint
from .users.controller import users
from .friends.controller import friends
from .extension import db, ma
from .model import Users, Friends, Posts, Comments, Likes
import os
from flask_jwt_extended import JWTManager


def create_db(app):
    if not os.path.exists("/instance/facebook.db"):
        with app.app_context():
            db.create_all()
        print("Create DB!!!")


def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    # Set up the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    db.init_app(app)
    ma.init_app(app)
    create_db(app)
    app.register_blueprint(users)
    app.register_blueprint(friends)

    return app
