# Wrapped/models.py
from django.db import models
from UserAuth.models import User
import json

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    artists = models.TextField(default='[]')
    tracks = models.TextField(default='[]')
    is_public = models.BooleanField(default=True)
    def set_top_artists(self, artists_data):
        self.artists = json.dumps(artists_data)
    def set_top_tracks(self, tracks_data):
        self.tracks = json.dumps(tracks_data)

    def get_top_artists(self):
        return json.loads(self.artists)
    def get_top_tracks(self):
        return json.loads(self.tracks)
    def __str__(self):
        return f"{self.user} - {self.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap = models.ForeignKey(SpotifyWrap, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} likes {self.wrap}"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"