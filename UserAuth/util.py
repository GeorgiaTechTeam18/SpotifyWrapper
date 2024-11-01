from .models import User, SpotifyToken
from django.utils import timezone
from datetime import timedelta
from requests import post
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(user: User):
    user_tokens = user.default_spotify_token
    print(f"user token {user_tokens}")
    if user_tokens:
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
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    # creates a new token if the email doesn't equal the current token's account email
    if tokens and (spotify_account_email is None or tokens.spotify_account_username == spotify_account_username):
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken.objects.create(user=user, access_token=access_token, refresh_token=refresh_token, token_type=token_type,
                              expires_in=expires_in)
        setEmailAndUsernameIfProvided(tokens, spotify_account_email,spotify_account_username)
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
    refresh_token = get_user_tokens(user).refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')

    update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token)
