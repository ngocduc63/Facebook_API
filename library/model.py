from .extension import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256))
    nickname = db.Column(db.String(256))
    birth_date = db.Column(db.Integer)
    avatar = db.Column(db.String(256))
    cover_photo = db.Column(db.String(256))
    gender = db.Column(db.Integer, nullable=False)
    role = db.Column(db.Integer)
    create_at = db.Column(db.Integer, nullable=False)

    def __init__(self, username, email, password_hash, description, nickname,
                 birth_date, avatar, cover_photo, gender, role, create_at):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.description = description
        self.nickname = nickname
        self.birth_date = birth_date
        self.avatar = avatar
        self.cover_photo = cover_photo
        self.gender = gender
        self.role = role
        self.create_at = create_at


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    create_at = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, friend_id,  create_at):
        self.user_id = user_id
        self.friend_id = friend_id
        self.create_at = create_at


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    image = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.Integer)
    isDeleted = db.Column(db.Integer)
    create_at = db.Column(db.Integer, nullable=False)

    def __init__(self, title, image, user_id, status, isDeleted, create_at):
        self.title = title
        self.image = image
        self.user_id = user_id
        self.status = status
        self.isDeleted = isDeleted
        self.create_at = create_at


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    content = db.Column(db.String(256))
    isDeleted = db.Column(db.Integer)
    create_at = db.Column(db.Integer, nullable=False)

    def __init__(self, title, user_id, post_id, content, isDeleted, create_at):
        self.title = title
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
        self.isDeleted = isDeleted
        self.create_at = create_at


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    isLiked = db.Column(db.Integer)
    create_at = db.Column(db.Integer, nullable=False)

    def __init__(self,  user_id, post_id, isLiked, create_at):
        self.user_id = user_id
        self.post_id = post_id
        self.isLiked = isLiked
        self.create_at = create_at