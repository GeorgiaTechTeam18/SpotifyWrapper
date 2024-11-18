# Wrapped/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, create_wrap, like_wrap, view_wrap

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view-wraps/', view_wraps, name='view_wraps'),
    path('create-wrap/', create_wrap, name='create_wrap'),
    path('view-wrap/wrap_id_<uuid:wrap_id>/', view_wrap, name='view_wrap'),
    path('like-wrap/<uuid:wrap_id>/', like_wrap, name='like_wrap'),
    path('create-wrap/time_range_<time_range>/', create_wrap, name='create_wrap')
]
