from django.urls import path
from portfolio import views as portfolio_views


urlpatterns = [
    path('projects/', portfolio_views.ProjectUploadListCreateView.as_view(), name='project-list'),
    path('projects/<int:pk>/', portfolio_views.ProjectUploadDetailView.as_view(), name='project-detail'),
    path('contact/', portfolio_views.ContactMessageCreateView.as_view(), name='contact-create'),
    path('contact/messages/', portfolio_views.ContactMessageListView.as_view(), name='contact-list'),
]

   