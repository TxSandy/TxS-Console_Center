from django.urls import path
from . import views

urlpatterns = [
    path('add-visitor/', views.add_visitor, name='add_visitor'),
    path('visitor-stats/', views.get_visitor_stats, name='visitor_stats'),
]
