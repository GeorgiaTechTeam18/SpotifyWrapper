from django.shortcuts import render, redirect
from rest_framework.response import Response
from requests import Request, post
from .util import update_or_create_user_tokens, is_spotify_authenticated
from .models import SpotifyToken
import os
from dotenv import load_dotenv

load_dotenv()

def home(request):
    is_authenticated = is_spotify_authenticated(request.session.session_key)
    return render(request, 'UserAuth/index.html', {'is_authenticated': is_authenticated})


def login(request):
    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': 'user-read-playback-state user-modify-playback-state user-read-currently-playing',
        'response_type': 'code',
        'redirect_uri': os.getenv('REDIRECT_URI'),
        'client_id': os.getenv('CLIENT_ID')
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

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv('REDIRECT_URI'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('home')


def isauthenticated(request):
    is_authenticated = is_spotify_authenticated(request.session.session_key)
    return Response({'status': is_authenticated})