from rest_framework import serializers
from .models import Post, Like, Comment
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class PostSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user = UserSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    # comment_count_value = serializers.ReadOnlyField(source='comment_count_value')  # Add this line
    comment_count_value = serializers.ReadOnlyField()  # Add this line

    # field to indicate whether the current user has liked the post
    # user_has_liked = serializers.SerializerMethodField()

    # Include comments for each post
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'video_url', 'created_at',
                  'updated_at', 'like_count', 'comment_count', 'comments', 'comment_count_value']

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        # Check if the user has liked the post
        if user and user.is_authenticated:
            return Like.objects.filter(post=obj, user=user).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
