# myapp/urls.py
from django.urls import path
from .views import post_wrap, view_wraps

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view-wraps/', view_wraps, name='view_wraps'),
]
