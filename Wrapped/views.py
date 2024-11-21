# Wrapped/views.py
import requests
from datetime import datetime
from django.http import JsonResponse, HttpResponseServerError, HttpResponseNotFound
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
    liked = request.GET.get('liked') == 'true'
    if liked:
        public_wraps = SpotifyWrap.objects.filter(is_public=True, liked_by=request.user)
    else:
        public_wraps = SpotifyWrap.objects.filter(is_public=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wraps_data = [{'id': wrap.id, 'title': wrap.title, 'csrf_token': request.COOKIES['csrftoken']} for wrap in
                      public_wraps]
        return JsonResponse({'wraps': wraps_data})

    return render(request, 'Wrapped/view_public_wraps.html', {"wraps": public_wraps})

def view_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return render(request, 'Wrapped/view_wraps.html', {"wraps": wraps})

def view_wrap(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, uuid=wrap_id)
    tracks = wrap.get_top_tracks()
    return render(request,'Wrapped/view_wrap.html',
                  {
                      "top_track":tracks[0],
                      "tracks":tracks[1:6],
                      "artists": wrap.get_top_artists()[:5],
                      "genres": wrap.get_top_genres()[:10],
                      "audio_features": wrap.get_audio_features(),
                  })

# TODO
def like_wrap(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, uuid=wrap_id)

    if request.user in wrap.liked_by.all():
        wrap.liked_by.remove(request.user)
        message = 'Unliked'
    else:
        wrap.liked_by.add(request.user)
        message = 'Liked'
    wrap.save()

    return JsonResponse({'message': message})


key_map = {
        0: 'C',
        1: 'C♯/D♭',
        2: 'D',
        3: 'D♯/E♭',
        4: 'E',
        5: 'F',
        6: 'F♯/G♭',
        7: 'G',
        8: 'G♯/A♭',
        9: 'A',
        10: 'A♯/B♭',
        11: 'B',
        -1: 'No key detected'
    }

def create_wrap(request, time_range = None):
    if request.method == 'GET' or time_range == None:
        return render(request, "Wrapped/choose_time_range.html")

    #time_range = request.POST.get('time_range')
    print(time_range)
    if isinstance(request.user, AnonymousUser):
        return redirect('/login?error=not_logged_in')

    access_token = get_user_tokens(request.user).access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    limit = 'limit=10'
    wrap_name = request.POST.get('name')
    if wrap_name == '' or wrap_name is None:
        user_profile_url = 'https://api.spotify.com/v1/me'
        user_profile_response = requests.get(user_profile_url, headers=headers)
        if user_profile_response.status_code == 200:
            profile = user_profile_response.json()
            username = profile.get('display_name', "Anonymous")
            time_range = request.POST.get('time_range')
            date = datetime.today()
            wrap_name = f"{username}'s wrapped over the last {time_range} months - {date}"

    print(wrap_name)

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
        print(artist_response.json())
        return HttpResponseNotFound('Failed to retrieve top artists. Try re-linking your spotify in the profile page')

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
                'preview_url': item.get('preview_url'),
                'id': item.get('id'),
            })
    else:
        return HttpResponseNotFound('Failed to retrieve top tracks. Try re-linking your spotify in the profile page')

    wrap, create = SpotifyWrap.objects.get_or_create(user=request.user, title= wrap_name)
    wrap.set_top_artists(artist_data)
    wrap.set_top_tracks(track_data)

    # Generate the Overall Mood by averaging the Audio Features of the top tracks
    # Fetch top tracks from Spotify API
    audio_features_endpoint = f'https://api.spotify.com/v1/audio-features?ids={",".join([track["id"] for track in track_data])}'
    audio_features_response = requests.get(audio_features_endpoint, headers=headers)
    audio_features = dict()
    audio_features_counted = dict()
    keys = [0] * 12
    if audio_features_response.status_code == 200:
        audio_features_data = audio_features_response.json()
        for item in audio_features_data.get('audio_features', []):
            for attr in ["danceability", "valence", "speechiness", "energy", "instrumentalness", "liveness", "loudness", "mode", "tempo", "popularity"]:
                if (item.get(attr) != None):
                    audio_features[attr] = audio_features.get(attr, 0) + item.get(attr)
                    audio_features_counted[attr] = audio_features_counted.get(attr, 0) + 1
            if (item.get("key") != None and item.get("key") != -1):
                keys[item.get("key")] += 1
    for key, value in audio_features.items():
        audio_features[key] = value / audio_features_counted.get(key, 1)

    audio_features["most_common_key"] = key_map[keys.index(min(keys))]

    wrap.set_audio_features(audio_features)
    wrap.save()
    return redirect(view_wrap, wrap_id=wrap.uuid)