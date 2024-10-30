# myapp/views.py
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')

def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')

def get_artists(request):
    access_token = request.user.social_auth.get(provider='spotify').extra_data['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    time_range = 'time_range=medium_term'
    limit = 'limit=10'
    endpoint = 'https://api.spotify.com/v1/me/top/artists?' + time_range + '&' + limit
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
        return JsonResponse({'status': 'success', 'data': artist_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to retrieve top items'})

    return render(request, 'myapp/get_artists.html')

def get_tracks(request):
    access_token = request.user.social_auth.get(provider='spotify').extra_data['access_token']

    headers = { 'Authorization': f'Bearer {access_token}' }
    time_range = 'time_range=medium_term'
    limit = 'limit=10'
    endpoint = 'https://api.spotify.com/v1/me/top/tracks?' + time_range + '&' + limit
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
        return JsonResponse({'status': 'success', 'data': track_data})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to retrieve top items'})

    return render(request, 'myapp/track_data.html')