from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class User(AbstractUser, PermissionsMixin):
    default_spotify_token = models.ForeignKey('SpotifyToken', on_delete=models.SET_NULL, related_name="default_spotify_token", null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class SpotifyToken(models.Model):
    user = models.ForeignKey(User,
                             models.SET_NULL,
                             blank=True,
                             null=True,)
    spotify_account_email = models.CharField(max_length=255, null=True, blank=True)
    spotify_account_username = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=255)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)
    profile_name = models.CharField(max_length=255)