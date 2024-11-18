# Wrapped/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, create_wrap, like_wrap, view_wrap, select_wraps_to_post, make_wraps_public, \
    view_public_wraps

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view-wraps/', view_wraps, name='view_wraps'),
    path('create-wrap/', create_wrap, name='create_wrap'),
    path('view-wrap/wrap_id_<uuid:wrap_id>/', view_wrap, name='view_wrap'),
    path('like-wrap/<uuid:wrap_id>/', like_wrap, name='like_wrap'),
    path('create-wrap/<time_range>/', create_wrap, name='create_wrap'),
    path('select-wraps-to-post/', select_wraps_to_post, name='select_wraps_to_post'),
    path('make-wraps-public/', make_wraps_public, name='make_wraps_public'),
    path('view-public-wraps/', view_public_wraps, name='view_public_wraps')
]
