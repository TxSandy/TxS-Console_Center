from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views


urlpatterns = [
    # Userauths API Endpoints
    path('user/token/', api_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', api_views.RegisterView.as_view(), name='auth_register'),
    path('user/profile/<user_id>/', api_views.ProfileView.as_view(), name='user_profile'),

    # Post Endpoints
    path('post/category/list/', api_views.CategoryListAPIView.as_view()),
    path('post/category/posts/<category_slug>/', api_views.PostCategoryListAPIView.as_view()),
    path('post/lists/', api_views.PostListAPIView.as_view()),
    path('post/detail/<slug>/', api_views.PostDetailAPIView.as_view()),
    path('post/like-post/', api_views.LikePostAPIView.as_view()),
    path('post/comment-post/', api_views.PostCommentAPIView.as_view()),
    path('post/bookmark-post/', api_views.BookmarkPostAPIView.as_view()),

    # Dashboard APIS
    path('author/dashboard/stats/<user_id>/', api_views.DashboardStats.as_view()),
    path('author/dashboard/post-list/<user_id>/', api_views.DashboardPostLists.as_view()),
    path('author/dashboard/comment-list/<user_id>/', api_views.DashboardCommentLists.as_view()),
    path('author/dashboard/notification-list/<user_id>/', api_views.DashboardNotificationsList.as_view()),
    path('author/dashboard/notification-mark-seen/', api_views.DashboardMarkNotificationAsSeen.as_view()),
    path('author/clear-notifications/', api_views.DashboardClearAllNotifications.as_view()),
    path('author/dashboard/reply-comment/', api_views.DashboardCommentAPIView.as_view()),
    path('author/dashboard/post-create/', api_views.DashboardPostCreateAPIView.as_view()),
    path('author/dashboard/post-detail/<user_id>/<post_id>/', api_views.DashboardPostEditAPIView.as_view()),

    #txsandy Dasboard
    path('blog/categories/create/', api_views.CategoryCreateAPIView.as_view(), name='category_create'),
    path('tags/', api_views.TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', api_views.TagUpdateDeleteView.as_view(), name='tag-update-delete'),
]