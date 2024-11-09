# myapp/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, deepcut

app_name = 'myapp'

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view_wraps/', view_wraps, name='view_wraps'),
    path('generate_wraps/', view_wraps, name='view_wraps'),
    path('deepcut/', deepcut, name='deepcut'),
]
