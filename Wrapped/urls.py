# Wrapped/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, create_wrap, like_wrap, view_wrap, select_wraps_to_post, make_wraps_public, \
    view_public_wraps

urlpatterns = [
    path('post_wrap/', post_wrap, name='post_wrap'),
    path('view_wraps/', view_wraps, name='view_wraps'),
    path('create_wrap/', create_wrap, name='create_wrap'),
    path('create_wrap/<str:time_range>', create_wrap, name='create_wrap'),
    path('view_wrap/wrap_id_<uuid:wrap_id>/', view_wrap, name='view_wrap'),
    path('like_wrap/<uuid:wrap_id>/', like_wrap, name='like_wrap'),
    path('select_wraps_to_post/', select_wraps_to_post, name='select_wraps_to_post'),
    path('make_wraps_public/', make_wraps_public, name='make_wraps_public'),
    path('view_public_wraps/', view_public_wraps, name='view_public_wraps')
]
