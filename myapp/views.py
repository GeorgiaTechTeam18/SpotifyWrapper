# myapp/views.py
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from UserAuth.util import get_user_tokens
from .models import SpotifyWrap


@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')

def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')

def get_top(request):
    if isinstance(request.user, AnonymousUser):
        return redirect('/login?error=spotify_auth_failed')
    access_token = get_user_tokens(request.user).access_token

    headers = {'Authorization': f'Bearer {access_token}'}
    time_range = 'time_range=medium_term'
    limit = 'limit=10'

    # Get top artists
    artist_endpoint = 'https://api.spotify.com/v1/me/top/artists?' + time_range + '&' + limit
    artist_response = requests.get(artist_endpoint, headers=headers)

    artist_data = []
    if artist_response.status_code == 200:
        top_artists = artist_response.json()
        for item in top_artists.get('items', []):
            artist_data.append({
                'image': item.get('images')[0].get('url'),
                'name': item.get('name'),
                'genres': item.get('genres'),
                'artist_url': item.get('external_urls').get('spotify')
            })

    # Get top tracks
    track_endpoint = 'https://api.spotify.com/v1/me/top/tracks?' + time_range + '&' + limit
    track_response = requests.get(track_endpoint, headers=headers)

    track_data = []
    if track_response.status_code == 200:
        top_tracks = track_response.json()
        for item in top_tracks.get('items', []):
            track_data.append({
                'artist_url': item.get('album').get('artists')[0].get('external_urls').get('spotify'),
                'artist_name': item.get('album').get('artists')[0].get('name'),
                'album_url': item.get('album').get('external_urls').get('spotify'),
                'album_image': item.get('album').get('images')[0].get('url'),
                'album_name': item.get('album').get('name'),
                'duration_ms': item.get('duration_ms'),
                'song_url': item.get('external_urls').get('spotify'),
                'song_name': item.get('name'),
                'preview_url': item.get('preview_url')
            })

    wrap = SpotifyWrap.objects.get_or_create(user=request.user, title="Spotify Wrapped")
    wrap.set_top_artists(artist_data)
    wrap.set_top_tracks(track_data)
    wrap.save()

    return render(request, 'myapp/get_top.html', {'artist_data': artist_data, 'track_data': track_data})