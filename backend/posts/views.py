from django.shortcuts import render

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Post, Upvote, Comment
from .serializers import PostSerializer, UpvoteSerializer, CommentSerializer
from django.contrib.auth.models import User

# Create your views here.

# provide the ability to fetch all the blog posts available and also will have the ability to create a new blog post
class PostListAPIView(APIView):
    # The permission_classes attribute of the PostListAPIView class specifies that only authenticated users are allowed to access this view
    permission_classes = [permissions.IsAuthenticated]

    # retrieves all the blog posts on the website and creates a serialized representation of the data using the PostSerializer class
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # creates a new Post object using the data from the request, serializes the data using the PostSerializer class, 
    # and returns the serialized data in an HTTP response with a status code of 201 CREATED
    def post(self, request, *args, **kwargs):
        data = {
            'user': request.user.id,
            'title': request.data.get('title'),
            'body': request.data.get('body')
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailAPIView(APIView):
    # The permission_classes attribute of the PostListAPIView class specifies that only authenticated users are allowed to access this view
    permission_classes = [permissions.IsAuthenticated]
    
    #  helper method that retrieves the post with the specified primary key (pk)
    def get_object(self, pk):
        try:
            return Post.objects.get(pk = pk)
        except Post.DoesNotExist:
            return None
    
    # uses the get_object method to retrieve the post with the specified pk, serializes the post using the PostSerializer class, 
    # and returns the serialized data in an HTTP response with a status code of 200 OK
    def get(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    # class is called when a PUT request is sent to the view. It uses the get_object method to retrieve the post with the specified pk, 
    # updates the post with the data from the request and saves the updated pos
    def put(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        data = {
            'user': request.user.id,
            'title': request.data.get('title'),
            'body': request.data.get('body'),
            'upvote_count': post.upvote_count
        }
        serializer = PostSerializer(post, data = data, partial = True)
        if serializer.is_valid():
            if post.user.id == request.user.id:
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response({"error": "You are not authorized to edit this post"}, status = status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    # uses the get_object method to retrieve the post with the specified pk and then deletes it 
    # if the current user is the owner of the post
    def delete(self, request, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error':'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        if post.user.id == request.user.id:
            post.delete()
            return Response({'res':'Object deleted!'}, status = status.HTTP_200_OK)
        return Response({'error':'You are not authorized to delete this post'}, status=status.HTTP_401_UNAUTHORIZED)
    
class UserPostAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # retrieves all the posts created by that user, and then creates a serialized representation of the data 
    # using the PostSerializer class.
    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username = username).first()
        if user is None:
            # If the user with the specified username does not exist, it returns an error
            return Response({'error' : 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(user = user)
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
class UpvoteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Post.objects.get(pk = pk)
        except Post.DoesNotExist:
            return None
        
    # uses the get_object method to retrieve the post with the specified pk and then either adds 
    # or removes an upvote for the post by the current user
    def post(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error' : 'Post not found'}, status = status.HTTP_404_NOT_FOUND)

        upvoters = post.upvotes.all().values_list('user', flat = True)
        if request.user.id in upvoters:
            post.upvote_count += 1
            post.upvotes.filter(user = request.user, post = post)
        else:
            post.upvote_count += 1
            upvote = Upvote(user = request.user, post = post)
            upvote.save()
        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CommentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None
        
    # uses the get_object method to retrieve the post with the specified pk, 
    # retrieves all the comments on that post, and then creates a serialized representation of the
    # data using the CommentSerializer class
    def get(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error':'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post = post)
        serializer = CommentSerializer(comments, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # uses the get_object method to retrieve the post with the specified pk, creates a new Comment object using the data 
    # from the request, serializes the data using the CommentSerializer class
    def post(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error':'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        data = {
            'user': request.user.id, 
            'post': post.id,
            'body': request.data.get('body')
        }
        serializer = CommentSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

