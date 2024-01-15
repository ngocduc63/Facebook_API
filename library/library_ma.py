from .extension import ma

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "password_hash", "description", "nickname",
                  "birth_date", "avatar", "cover_photo", "gender", "role", "create_at")

class FriendSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "friend_id", "create_at")

class PostSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "image", "user_id", "status", "isDelete", "create_at")

class CommentSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "post_id", "content", "isDeleted", "create_at")

class LikeSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "post_id", "isLiked", "create_at")