from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('authWithSpotify/', views.authWithSpotify, name='authWithSpotify'),
    path('callback/', views.callback, name='callback'),
    path('is-authenticated/', views.isauthenticated, name='is-authenticated'),
    path('profile/', views.profile_view, name='profile')
]