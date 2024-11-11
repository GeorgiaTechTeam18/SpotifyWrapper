from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('authWithSpotify/', views.authWithSpotify, name='authWithSpotify'),
    path('callback/', views.callback, name='callback'),
    path('profile/', views.profile_view, name='profile'),
    path('unlink/', views.delete_token, name='unlink_token'),
    path('deepcut/', include('myapp.urls'), name='deepcut'),
    path('view_wraps/', include('myapp.urls'), name='view_wraps')
]