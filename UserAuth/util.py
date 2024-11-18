from .models import User, SpotifyToken
from django.utils import timezone
import datetime
from requests import post, get
import os
from dotenv import load_dotenv
from functools import cache

load_dotenv()

BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(user: User):
    user_tokens = user.default_spotify_token
    print(f"user token {user_tokens}")
    if user_tokens:
        expiry = user_tokens.expires_in
        if expiry <= timezone.now():
            return refresh_spotify_token(user)
        return user_tokens
    else:
        return None


def setEmailAndUsernameIfProvided(tokens, email, username):
    if (email != None and username != None):
        tokens.spotify_account_email = email
        tokens.spotify_account_username = username
        tokens.save(update_fields=['spotify_account_username', 'spotify_account_email'])


def update_or_create_user_tokens(user: User, access_token, token_type, expires_in, refresh_token,
                                 spotify_account_email=None, spotify_account_username=None):
    tokens = get_user_tokens(user)
    expires_in = timezone.now() + datetime.timedelta(seconds=expires_in)

    # creates a new token if the email doesn't equal the current token's account email
    if tokens and (spotify_account_email is None or tokens.spotify_account_username == spotify_account_username):
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken.objects.create(user=user, access_token=access_token, refresh_token=refresh_token,
                                             token_type=token_type,
                                             expires_in=expires_in)
        setEmailAndUsernameIfProvided(tokens, spotify_account_email, spotify_account_username)
        user.default_spotify_token = tokens
        user.save()


def is_spotify_authenticated(user: User):
    tokens = get_user_tokens(user)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(user)
        return True
    return False


def refresh_spotify_token(user: User):
    token = user.default_spotify_token
    refresh_token = token.refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    }).json()

    print(response)

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')

    expires_in = timezone.now() + datetime.timedelta(seconds=expires_in)

    token.access_token = access_token
    token.expires_in = expires_in
    token.token_type = token_type
    token.save(update_fields=['access_token', 'expires_in', 'token_type'])

    return token


saved_sever_token = {
    'expires': datetime.datetime.now(),
    'token': "",
}


def get_server_spotify_token(force_refresh=False):
    global saved_sever_token
    if (saved_sever_token["expires"] > datetime.datetime.now() or force_refresh):
        return saved_sever_token["token"]

    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'data': {
            'grant_type': 'client_credentials',
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET')
        },
        'json': True
    }

    response = post(**auth_options)

    if response.status_code == 200:
        response_data = response.json()
        token = response_data['access_token']
        saved_sever_token = {
            'expires': datetime.datetime.now() + datetime.timedelta(seconds=response_data['expires_in']),
            'token': token,
        }
        return token
    return None

@cache
def get_top_song_album_covers():
    token = get_server_spotify_token()

    response = get(
        'https://api.spotify.com/v1/playlists/37i9dQZEVXbLRQDuF5jeBp?fields=tracks.items(track(album(name,id,images)))',
        headers={"Authorization": f"Bearer {token}"}
    ).json()

    return [x["track"]["album"] for x in response["tracks"]["items"][0:10]]
