# myapp/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, get_artists, get_tracks

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view-wraps/', view_wraps, name='view_wraps'),
    path('get-artists/', get_artists, name='get_artists'),
    path('get-tracks/', get_tracks, name='get_tracks'),
]
