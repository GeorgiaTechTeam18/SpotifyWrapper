# Wrapped/models.py
from django.db import models
from UserAuth.models import User
import json
import uuid

class SpotifyWrap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    artists = models.TextField(default='[]')
    tracks = models.TextField(default='[]')
    audio_features = models.TextField(default='{}')
    is_public = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    def set_top_artists(self, artists_data):
        self.artists = json.dumps(artists_data)
    def set_top_tracks(self, tracks_data):
        self.tracks = json.dumps(tracks_data)
    def set_audio_features(self, tracks_data):
        self.audio_features = json.dumps(tracks_data, ensure_ascii=False)
    def get_top_artists(self):
        return json.loads(self.artists)
    def get_top_tracks(self):
        return json.loads(self.tracks)
    def get_top_genres(self, num_artists=50):
        artists = json.loads(self.artists)
        genres = dict()
        for artist in artists[:num_artists]:
            for genre in artist['genres']:
                genres[genre] = genres.get(genre, 0) + 1
                # some genres get missed by spotify being too specific
                if not genre in ["rap", "rock", "hip hop", "pop", "jazz", "punk", "country", "classical"]:
                    for large_genre in ["rap", "rock", "hip hop", "pop", "jazz", "punk", "country", "classical"]:
                        if large_genre in genre:
                            genres[large_genre] = genres.get(large_genre, 0) + 1
        return sorted(genres.items(), key=lambda kv: kv[1], reverse=True)
    def get_audio_features(self):
        return json.loads(self.audio_features)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap = models.ForeignKey(SpotifyWrap, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='followed', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)