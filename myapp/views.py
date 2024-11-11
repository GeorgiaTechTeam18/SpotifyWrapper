# myapp/views.py
import requests
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from UserAuth.util import get_user_tokens
from .models import SpotifyWrap


@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')

def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')

def get_artists(request, time_range='medium_term'):
    access_token = get_user_tokens(request.user).access_token

    headers = {'Authorization': f'Bearer {access_token}'}
    limit = 'limit=10'
    endpoint = f'https://api.spotify.com/v1/me/top/artists?time_range={time_range}&{limit}'
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        top_items = response.json()
        artist_data = []
        for item in top_items.get('items', []):
            artist_data.append({
                'image': item.get('images')[0].get('url'),
                'name': item.get('name'),
                'genres': item.get('genres'),
                'artist_url': item.get('external_urls').get('spotify')
            })
        return render(request, 'myapp/get-artists.html', {'artist_data': artist_data})
    else:
        return render(request, 'myapp/get-artists.html', {'error': 'Failed to retrieve top artists.'})


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




def get_tracks(request, time_range='medium_term'):
    access_token = get_user_tokens(request.user).access_token

    headers = {'Authorization': f'Bearer {access_token}'}
    limit = 'limit=10'
    endpoint = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&{limit}'
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        top_items = response.json()
        track_data = []
        for item in top_items.get('items', []):
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
        return render(request, 'myapp/get_tracks.html', {'track_data': track_data})
    else:
        return render(request, 'myapp/get_tracks.html', {'error': 'Failed to retrieve top tracks.'})




