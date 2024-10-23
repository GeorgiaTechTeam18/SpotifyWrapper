import secrets
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from rest_framework.response import Response
from requests import Request, post, exceptions
from .util import update_or_create_user_tokens, is_spotify_authenticated
from .models import SpotifyToken
import os
from dotenv import load_dotenv

load_dotenv()

STATE_KEY = os.getenv('STATE_KEY')
REDIRECT_URI = os.getenv('REDIRECT_URI')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def home(request):
    is_authenticated = is_spotify_authenticated(request.session.session_key)
    return render(request, 'UserAuth/index.html', {'is_authenticated': is_authenticated})

def generate_random_string(length):
    return secrets.token_hex(length // 2)

def login(request):
    state = generate_random_string(16)
    request.session[STATE_KEY] = state

    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing',
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'state': state
    }).prepare().url

    return redirect(url)


def logout(request):
    if request.session.exists(request.session.session_key):
        session_id = request.session.session_key
        SpotifyToken.objects.filter(user=session_id).delete()
        request.session.flush()

    return redirect('home')


def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    stored_state = request.session.get(STATE_KEY)

    if state is None or state != stored_state:
        return redirect(f"/?{urlencode({'error': 'state_mismatch'})}")

    if STATE_KEY in request.session:
        del request.session[STATE_KEY]

    try:
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        })
        response.raise_for_status()
    except exceptions.RequestException as e:
        return redirect(f"/?{urlencode({'error': 'token_request_failed'})}")

    response_data = response.json()
    access_token = response_data.get('access_token')
    token_type = response_data.get('token_type')
    refresh_token = response_data.get('refresh_token')
    expires_in = response_data.get('expires_in')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('home')


def isauthenticated(request):
    is_authenticated = is_spotify_authenticated(request.session.session_key)
    return Response({'status': is_authenticated})