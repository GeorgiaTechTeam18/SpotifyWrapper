# myapp/models.py
from django.db import models
from UserAuth.models import User

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artists = models.TextField(default='')
    tracks = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap = models.ForeignKey(SpotifyWrap, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Artist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    genres = models.JSONField()
    image_url = models.URLField()
    artist_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    time_range = models.CharField(max_length=50)

class Track(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    duration_ms = models.IntegerField()
    song_url = models.URLField()
    preview_url = models.URLField(null=True, blank=True)
    album_image_url = models.URLField()
    artist_url = models.URLField()
    album_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    time_range = models.CharField(max_length=50)