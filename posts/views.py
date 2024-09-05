from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import AnonymousUser, User

from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session

from rest_framework.decorators import api_view, permission_classes
from django.db import models

from django.db.models import Count, Subquery
from django.db.models.functions import Coalesce



class RecentPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    # Adjust the number of posts as needed
    queryset = Post.objects.all().order_by('-created_at')[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostListViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Set the user for the new post
        serializer.save(user=self.request.user)


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


# class PostListView(generics.ListAPIView):
#     serializer_class = PostSerializer
#     queryset = Post.objects.all()

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update({'request': self.request})
#         return context


class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Get the post ID from the URL
        post_id = self.kwargs.get('post_id', None)
        # print(post_id)

        # Check if the post exists
        post = get_object_or_404(Post, pk=post_id)
        # print(post)

        # Associate the like with the current user and the post
        serializer.save(user=self.request.user, post=post)

        # Update the like count in the associated post
        post.like_count += 1
        post.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserHasLikedView(generics.RetrieveAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, *args, **kwargs):
        # Check if the post exists
        post = get_object_or_404(Post, pk=post_id)

        # Check if the user has liked the post
        user_has_liked = Like.objects.filter(
            post=post, user=request.user).exists()

        return Response({'user_has_liked': user_has_liked}, status=status.HTTP_200_OK)


class UnlikePostView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, *args, **kwargs):
        # Check if the post exists
        post = get_object_or_404(Post, pk=post_id)

        # Check if the user has liked the post
        like = Like.objects.filter(post=post, user=request.user).first()

        if like:
            # Delete the like
            like.delete()

            # Update the like count in the associated post
            post.like_count -= 1
            post.save()

            return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User has not liked the post'}, status=status.HTTP_400_BAD_REQUEST)


class UserLikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve posts liked by the current user
        liked_posts = Post.objects.filter(like__user=self.request.user)
        return liked_posts


class LeastLikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve liked posts with the least like count
        least_liked_posts = Post.objects.annotate(
            total_likes=models.Count('like')).order_by('total_likes')
        return least_liked_posts


class AllLikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve all posts that have been liked
        liked_posts = Post.objects.filter(like__isnull=False)
        return liked_posts


class TopLikedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve liked posts with the highest like count
        # liked_posts = Post.objects.annotate(like_count=models.Count('like')).order_by('-like_count')
        liked_posts = Post.objects.annotate(
            total_likes=models.Count('like')).order_by('-total_likes')
        return liked_posts


class UnlikedPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        liked_post_ids = Like.objects.filter(
            user=user).values_list('post__id', flat=True)
        return Post.objects.exclude(id__in=liked_post_ids)


class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):  # Rename pk to post_id
        post = get_object_or_404(Post, pk=post_id)
        content = request.data.get('content', '')
        Comment.objects.create(user=request.user, post=post, content=content)
        return Response({'message': 'Comment added successfully'})


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        print("post id: ", post_id)
        post = get_object_or_404(Post, id=post_id)
        print("post: ", post)
        serializer.save(user=self.request.user, post=post)


class UserCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the authenticated user
        user = self.request.user
        # Return all comments by the authenticated user
        return Comment.objects.filter(user=user)


class UserCommentedPostsView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch posts on which the current user has commented
        user_commented_posts = Post.objects.filter(
            comment__user=request.user).distinct()
        serializer = PostSerializer(user_commented_posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AllCommentsListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


class UncommentedPostListView(APIView):
    def get(self, request, *args, **kwargs):
        uncommented_posts = Post.objects.filter(comment_count=0)
        serializer = PostSerializer(uncommented_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostCommentCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, format=None):
        # Retrieve the post based on post_id
        post = get_object_or_404(Post, id=post_id)
        # Count the comments for the post
        comment_count = Comment.objects.filter(post=post).count()
        # Return the comment count in the response
        return Response({'comment_count': comment_count})


class CommentBelongsToUserView(APIView):
    """
    Check if the comment belongs to the authenticated user.
    """

    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if the comment belongs to the authenticated user
        if request.user == comment.user:
            return Response({'belongs_to_user': True}, status=status.HTTP_200_OK)
        else:
            return Response({'belongs_to_user': False}, status=status.HTTP_200_OK)


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if the current user is the owner of the comment
        if comment.user != self.request.user:
            self.permission_denied(self.request)

        return comment


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the post based on post_id
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        # Return all comments for the specified post
        return Comment.objects.filter(post=post)


class MyPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)


class AddPostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        # Include the current user in the serializer context
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TopCommentedPostsView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve top commented posts
            top_commented_posts = Post.objects.annotate(
                comment_count_value=Count('comments')).order_by('-comment_count_value')[:5]

            # Serialize the posts
            serializer = PostSerializer(top_commented_posts, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePostView(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Override the default get_object to include user check
        obj = super().get_object()
        if obj.user == self.request.user:
            return obj
        raise PermissionDenied(
            "You don't have permission to update this post.")

    def get(self, request, *args, **kwargs):
        # Retrieve the current object data
        current_object = self.get_object()
        serializer = self.get_serializer(current_object)
        return Response(serializer.data)


class DeletePostView(APIView):
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        # Check if the user making the request is the owner of the post
        if request.user != post.user:
            return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
