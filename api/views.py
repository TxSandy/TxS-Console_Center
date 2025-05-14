from django.db.models import Sum
from django.shortcuts import get_object_or_404
# Restframework
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import  APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



# Custom Imports
from api import serializer as api_serializer
from api import models as api_models
from portfolio import models as portfolio_models
from portfolio.models import Tag

from django.http import HttpResponse


def home(request):
    return HttpResponse("Welcome to the TxSandy API!")


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = api_models.User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        profile = api_models.Profile.objects.get(user=user)
        return profile

class CategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Category.objects.all()
    

class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs['category_slug'] 
        category = get_object_or_404(api_models.Category, slug=category_slug)
        return api_models.Post.objects.filter(category=category, status="Active")
    
class PostListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Post.objects.filter(status="Active")

    
class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        post = api_models.Post.objects.get(slug=slug, status="Active")
        post.view += 1
        post.save()
        return post
    
class LikePostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'post_id': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
     
    
     
    def post(self, request):
        user_id = request.data['user_id']
        post_id = request.data['post_id']

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message" : "Post Disliked"}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)

            api_models.Notification.objects.create(
                user=post.user,
                post=post,
                type="Like"
            )
            return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)
        
class PostCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'comment': openapi.Schema(type=openapi.TYPE_STRING),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER, description='Optional parent comment ID'),
            },
            required=['post_id', 'name', 'email', 'comment']
        )
    )
    def post(self, request):
        post_id = request.data.get('post_id')
        name = request.data.get('name')
        email = request.data.get('email')
        comment = request.data.get('comment')
        parent_id = request.data.get('parent')

        try:
            post = api_models.Post.objects.get(id=post_id)
        except api_models.Post.DoesNotExist:
            raise NotFound("Post not found.")

        parent_comment = None
        if parent_id:
            try:
                parent_comment = api_models.Comment.objects.get(id=parent_id)
                if parent_comment.parent:
                    return Response({"message": "Replies to replies are not allowed."}, status=status.HTTP_400_BAD_REQUEST)
            except api_models.Comment.DoesNotExist:
                return Response({"message": "Parent comment not found."}, status=status.HTTP_400_BAD_REQUEST)

        comment_obj = api_models.Comment.objects.create(
            post=post,
            name=name,
            email=email,
            comment=comment,
            parent=parent_comment
        )

        # Optional notification
        api_models.Notification.objects.create(
            user=post.user,
            post=post,
            type="Comment"
        )

        return Response({
            "message": "Comment Sent",
            "comment": {
                "id": comment_obj.id,
                "post": comment_obj.post.id,
                "parent": comment_obj.parent.id if comment_obj.parent else None,
                "name": comment_obj.name,
                "email": comment_obj.email,
                "comment": comment_obj.comment,
                "date": comment_obj.date,
            }
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        post_id = request.query_params.get("post_id")
        if not post_id:
            return Response({"message": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = api_models.Post.objects.get(id=post_id)
        except api_models.Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get only top-level comments
        comments = api_models.Comment.objects.filter(post=post, parent=None).order_by('-date')

        def get_comment_data(comment):
            return {
                "id": comment.id,
                "name": comment.name,
                "email": comment.email,
                "comment": comment.comment,
                "date": comment.date,
                "replies": [
                    {
                        "id": reply.id,
                        "name": reply.name,
                        "email": reply.email,
                        "comment": reply.comment,
                        "date": reply.date,
                    }
                    for reply in comment.replies.all().order_by('-date')
                ]
            }

        comment_data = [get_comment_data(c) for c in comments]

        return Response(comment_data, status=status.HTTP_200_OK)
    
class BookmarkPostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'post_id': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    
    def post(self, request):
        user_id = request.data['user_id']
        post_id = request.data['post_id']

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        bookmark = api_models.Bookmark.objects.filter(post=post, user=user).first()
        if bookmark:
            bookmark.delete()
            return Response({"message": "Post Un-Bookmarked"}, status=status.HTTP_200_OK)
        else:
            api_models.Bookmark.objects.create(
                user=user,
                post=post
            )
            api_models.Notification.objects.create(
                user=post.user,
                post=post,
                type="Bookmark",
            )
            return Response({"message": "Post Bookmarked"}, status=status.HTTP_201_CREATED)
        
class DashboardStats(generics.ListAPIView):
    serializer_class = api_serializer.AuthorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        views = api_models.Post.objects.filter(user=user).aggregate(view=Sum("view"))['view']
        posts = api_models.Post.objects.filter(user=user).count()
        likes = api_models.Post.objects.filter(user=user).aggregate(total_likes=Sum("likes"))['total_likes']
        bookmarks = api_models.Bookmark.objects.all().count()
        categories = api_models.Category.objects.all().count()
        tags = portfolio_models.Tag.objects.all().count()
        projects = portfolio_models.ProjectUpload.objects.all().count()
        users = api_models.User.objects.all().count()
        comments = api_models.Comment.objects.all().count()


        return [{
            "views":views,
            "posts":posts,
            "likes":likes,
            "bookmarks":bookmarks,
            "categories":categories,
            "tags":tags,
            "projects": projects,
            "users":users,
            "comments":comments,
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class DashboardPostLists(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Post.objects.filter(user=user).order_by("-id")


    
class DashboardCommentLists(generics.ListAPIView):
    serializer_class = api_serializer.CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Comment.objects.filter(post__user=user)
    
class DashboardNotificationsList(generics.ListAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Notification.objects.filter(seen=False, user=user)

    
class DashboardMarkNotificationAsSeen(APIView):
    def post(self, request):
        notification_id = request.data['notification_id']
        notification = api_models.Notification.objects.get(id=notification_id)

        notification.seen = True
        notification.save()

        return Response({"message" : "Notification marked as seen"}, status=status.HTTP_200_OK)
    
class DashboardCommentAPIView(APIView):
    def post(self, request):
        comment_id = request.data['comment_id']
        reply = request.data['reply']

        comment = api_models.Comment.objects.get(id=comment_id)
        comment.reply = reply
        comment.save()

        return Response({"message": "Comment response sent"}, status=status.HTTP_201_CREATED)
    
class DashboardPostCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data)

        user_id = request.data.get("user_id")
        title = request.data.get("title")
        image = request.FILES.get("image")
        description = request.data.get("description")
        tag_names = request.data.get("tags", "").split(",")
        category_id = request.data.get("category")
        post_status = request.data.get("status")
        slug = request.data.get("slug")

        try:
            user = api_models.User.objects.get(id=user_id)
            category = api_models.Category.objects.get(id=category_id)
            profile = user.profile 
        except (api_models.User.DoesNotExist, api_models.Category.DoesNotExist):
            return Response({"error": "User or Category not found."}, status=400)
        except api_models.Profile.DoesNotExist:
            profile = None  

        post = api_models.Post.objects.create(
            user=user,
            profile=profile,  
            title=title,
            image=image,
            description=description,
            category=category,
            status=post_status,
            slug=slug,
        )

        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag_obj, _ = portfolio_models.Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag_obj)

        post.save()
        return Response({'message': "Post Created Successfully"}, status=status.HTTP_201_CREATED)

    
class DashboardPostEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id  =self.kwargs['user_id']
        post_id  =self.kwargs['post_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Post.objects.get(id=post_id, user=user)
    
    def update(self, request, *args, **kwargs):
        post_instance = self.get_object()

        title = request.data.get("title")
        image = request.data.get("image")
        description = request.data.get("description")
        tags = request.data.get("tags")
        category_id = request.data.get("category_id")
        post_status = request.data.get("post_status")

        category = api_models.Category.objects.geet(id=category_id)
        post_instance.title = title
        if image != "undefined":
            post_instance.image = image

        post_instance.description = description
        post_instance.tags = tags
        post_instance.category = category
        post_instance.status = post_status
        post_instance.save()

        return Response({"message": "Post updated successfully"}, status=status.HTTP_200_OK)
    

class CategoryCreateAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = api_serializer.CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TagListCreateView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = api_serializer.TagSerializer(tags, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = api_serializer.TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TagUpdateDeleteView(APIView):
    def put(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = api_serializer.TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DashboardClearAllNotifications(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        api_models.Notification.objects.filter(user_id=user_id).update(seen=True)
        return Response({"message": "All notifications cleared"}, status=200)


