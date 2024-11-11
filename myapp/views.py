# myapp/views.py
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from UserAuth.util import get_user_tokens
from .models import SpotifyWrap


@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')


def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')


def like_wrap(request):
    access_token = get_user_tokens(request.user).access_token
    wrap_id = request.POST.get('wrap_id')
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)

    # Check if wrap is already liked
    if request.user in wrap.likes.all():
        return JsonResponse({'message': 'already liked'})
    else:
        wrap.likes.add(request.user)
        return JsonResponse({'message': 'success'})


def unlike_wrap(request):
    access_token = get_user_tokens(request.user).access_token
    wrap_id = request.POST.get('wrap_id')
    wrap = SpotifyWrap.objects.get(id=wrap_id)

    # Check if unliked wrap is already liked
    if request.user in wrap.likes.all():
        wrap.likes.remove(request.user)
        return JsonResponse({'message': 'success'})
    else:
        return JsonResponse({'message': 'not liked'})


def get_top(request, time_range='medium_term'):
    if isinstance(request.user, AnonymousUser):
        return redirect('/login?error=not_logged_in')

    access_token = get_user_tokens(request.user).access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    limit = 'limit=10'

    # Fetch top artists from Spotify API
    artist_endpoint = f'https://api.spotify.com/v1/me/top/artists?time_range={time_range}&{limit}'
    artist_response = requests.get(artist_endpoint, headers=headers)
    artist_data = []
    if artist_response.status_code == 200:
        top_artists = artist_response.json()
        for item in top_artists.get('items', []):
            artist_data.append({
                'image_url': item.get('images')[0].get('url') if item.get('images') else '',
                'name': item.get('name'),
                'genres': item.get('genres'),
                'artist_url': item.get('external_urls', {}).get('spotify', '')
            })
    else:
        return render(request, 'myapp/get_top.html', {'error': 'Failed to retrieve top artists.'})

    # Fetch top tracks from Spotify API
    track_endpoint = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&{limit}'
    track_response = requests.get(track_endpoint, headers=headers)
    track_data = []
    if track_response.status_code == 200:
        top_tracks = track_response.json()
        for item in top_tracks.get('items', []):
            track_data.append({
                'artist_url': item.get('album').get('artists')[0].get('external_urls', {}).get('spotify', ''),
                'artist_name': item.get('album').get('artists')[0].get('name'),
                'album_url': item.get('album').get('external_urls', {}).get('spotify', ''),
                'album_image_url': item.get('album').get('images')[0].get('url') if item.get('album').get('images') else '',
                'album_name': item.get('album').get('name'),
                'duration_ms': item.get('duration_ms'),
                'song_url': item.get('external_urls', {}).get('spotify', ''),
                'song_name': item.get('name'),
                'preview_url': item.get('preview_url')
            })
    else:
        return render(request, 'myapp/get_top.html', {'error': 'Failed to retrieve top tracks.'})

    wrap, create = SpotifyWrap.objects.get_or_create(user=request.user, title="Spotify Wrapped")
    wrap.set_top_artists(artist_data)
    wrap.set_top_tracks(track_data)
    wrap.save()

    return render(request, 'myapp/get_top.html', {'artist_data': artist_data, 'track_data': track_data})