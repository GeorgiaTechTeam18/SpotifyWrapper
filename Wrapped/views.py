# Wrapped/views.py
import requests
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.http import require_POST
from UserAuth.util import get_user_tokens, refresh_spotify_token
from .models import SpotifyWrap


@login_required
def post_wrap(request):
    return render(request, 'Wrapped/post_wrap.html')

def select_wraps_to_post(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return render(request, 'Wrapped/select_wraps_to_post.html', {"wraps": wraps})

def make_wraps_public(request):
    wrap_ids = request.POST.getlist('wrap_ids')
    wraps = SpotifyWrap.objects.filter(id__in=wrap_ids, user=request.user)
    wraps.update(is_public=True)
    return redirect('view_public_wraps')

def view_public_wraps(request):
    public_wraps = SpotifyWrap.objects.filter(is_public=True)
    return render(request, 'Wrapped/view_public_wraps.html', {"wraps": public_wraps})

def view_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return render(request, 'Wrapped/view_wraps.html', {"wraps": wraps})

def view_wrap(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, pk=wrap_id)
    tracks = wrap.get_top_tracks()
    return render(request,'Wrapped/view_wrap.html',
                  {
                      "top_track":tracks[0],
                      "tracks":tracks[1:6],
                      "artists": wrap.get_top_artists()[:5],
                      "genres": wrap.get_top_genres()[:10]
                  })

# TODO
def like_wrap(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)

    # Check if wrap is already liked and if so unlike it (always toggle)
    return JsonResponse({'message': 'not yet working'})


def create_wrap(request, time_range='medium_term'):
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
        return HttpResponseServerError(request, 'Wrapped/get_top.html', {'error': 'Failed to retrieve top artists. Try re-linking your spotify in the profile page'})

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
        return HttpResponseServerError(request, 'Wrapped/get_top.html', {'error': 'Failed to retrieve top artists. Try re-linking your spotify in the profile page'})

    wrap, create = SpotifyWrap.objects.get_or_create(user=request.user, title="Spotify Wrapped")
    wrap.set_top_artists(artist_data)
    wrap.set_top_tracks(track_data)
    wrap.save()

    return view_wrap(request, wrap.id)