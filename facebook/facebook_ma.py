from .extension import ma
from flask_marshmallow import fields


class UserSchema(ma.Schema):
    class Meta:
        fields = ('_sa_instance_state', 'id', 'email', 'username', 'description', 'nickname',
                  'birth_date', 'avatar', 'cover_photo', 'gender', 'role', 'is_block', 'create_at', 'count_notification')
        exclude = ('_sa_instance_state',)


class FriendSchema(ma.Schema):
    class Meta:
        fields = ('_sa_instance_state', "id", "user_id", "friend_id", "is_accept", "create_at")
        exclude = ('_sa_instance_state',)


class PostSchema(ma.Schema):
    class Meta:
        fields = ('_sa_instance_state', "id", "title", "image", "user_id", "status", "isDelete", "create_at", 'category')
        exclude = ('_sa_instance_state',)


class CommentSchema(ma.Schema):
    class Meta:
        fields = ('_sa_instance_state', "id", "user_id", "post_id", "content", "isDeleted", "create_at")
        exclude = ('_sa_instance_state',)


class LikeSchema(ma.Schema):
    class Meta:
        fields = ('_sa_instance_state', "id", "user_id", "post_id", "category", "create_at")
        exclude = ('_sa_instance_state',)

