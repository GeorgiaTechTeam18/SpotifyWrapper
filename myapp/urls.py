# myapp/urls.py
from django.urls import path
from .views import post_wrap, view_wraps, deepcut, generate_wraps

app_name = 'myapp'

urlpatterns = [
    path('post-wrap/', post_wrap, name='post_wrap'),
    path('view_wraps/', view_wraps, name='view_wraps'),
    path('generate_wraps/', generate_wraps, name='generate_wraps'),
    path('deepcut/', deepcut, name='deepcut'),
]
