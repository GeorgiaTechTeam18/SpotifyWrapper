# Wrapped/views.py
import functools

import requests
from datetime import datetime
from django.http import JsonResponse, HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

from UserAuth.models import SpotifyToken
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

def norm_audio_features(audio_features: dict) -> (dict, dict):
    audio_features_graphs = {}
    audio_features_list = {}
    for key, value in audio_features.items():
        if (key in ["most_common_key", "tempo"]):
            audio_features_list[key] = value
        elif (key == "mode"):
            audio_features_graphs["minor vs major"] = int(value * 100)
        elif (key == "loudness"):
            audio_features_graphs["loudness"] = int((value + 60) / .6)
        elif (key == "valence"):
            audio_features_graphs["sad vs happy"] = int(value * 100)
        else:
            audio_features_graphs[key] = int(value*100)
    return audio_features_graphs, audio_features_list

def view_wrap(request, wrap_id):
    wrap = get_object_or_404(SpotifyWrap, uuid=wrap_id)
    tracks = wrap.get_top_tracks()
    genres = wrap.get_top_genres()[:10]
    max_genre = 0
    for genre in genres:
        max_genre = max(max_genre, genre[1])

    audio_features_graphs, audio_features_list = norm_audio_features(wrap.get_audio_features())
    return render(request,'Wrapped/view_wrap.html',
                  {
                      "wrap_title": wrap.title,
                      "top_track":tracks[0],
                      "tracks":tracks[1:6],
                      "artists": wrap.get_top_artists()[:5],
                      "genres": genres,
                      "max_genre": max_genre,
                      "audio_features_graphs": audio_features_graphs,
                      "audio_features_list": audio_features_list,
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

time_range_lookup = {"short_term": "month", "medium_term": "6 months", "long_term": "year"}

def create_wrap(request, time_range = None):
    if isinstance(request.user, AnonymousUser):
        return redirect('/login?error=not_logged_in')


    if request.method == 'GET' or time_range == None:
        if (request.user.default_spotify_token == None):
            associated_spotify_tokens = SpotifyToken.objects.filter(user__username=request.user.username)
            first_token = associated_spotify_tokens.first()
            if (first_token != None):
                request.user.default_spotify_token = first_token
                request.user.save()
            else:
                #when there is a user but there is not spotify token redirect to the profile page with a message
                return redirect('/profile?error=you are seeing this page because you need to link a spotify account with your account')
        return render(request, "Wrapped/choose_time_range.html")

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
            date = f'{datetime.today():%B %d, %Y}'
            wrap_name = f"{username}'s wrapped over the last {time_range_lookup[time_range]} - {date}"

    print(wrap_name)
    print("time_range " + time_range)

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
        print(artist_response.text)
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