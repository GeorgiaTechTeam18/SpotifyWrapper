import os
import secrets

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from dotenv import load_dotenv
from requests import Request, exceptions, post

from .form import ContactUsForm, RegistrationForm
from .models import SpotifyToken
from .util import get_top_song_album_covers, update_or_create_user_tokens

load_dotenv()

REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

User = get_user_model()


def home(request):
    return render(request, "UserAuth/index.html",
                  {"album_covers": get_top_song_album_covers()})


def contact(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Thank you for your feedback! We'll get back to you soon.")
            return redirect("contact")
    else:
        form = ContactUsForm()
    return render(request, "UserAuth/contactus.html", {"form": form})


def generate_random_string(length):
    return secrets.token_hex(length // 2)


def authWithSpotify(request):
    url = (
        Request(
            "GET",
            "https://accounts.spotify.com/authorize",
            params={
                "scope": "user-read-email user-top-read",
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
            },
        )
        .prepare()
        .url
    )

    return redirect(url)


def login_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            user = authenticate(
                request,
                username=user_data.get("email"),
                password=user_data.get("password"),
            )
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(
                    request, "Invalid email or password. Please try again.")
                return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "UserAuth/login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        print(form)
        if form.is_valid():
            user_data = form.cleaned_data
            user = User.objects.create_user(
                username=user_data.get("email"),
                password=user_data.get("password"))
            if user is not None:
                login(request, user)
                return redirect("home")
            return redirect("signup")
    else:
        form = RegistrationForm()

    return render(request, "UserAuth/signup.html", {"form": form})


@login_required()
def profile_view(request):
    error_message = (
        [] if request.GET.get("error") is None else [request.GET.get("error")]
    )
    associated_spotify_tokens = SpotifyToken.objects.filter(
        user__username=request.user.username
    )
    return render(
        request,
        "UserAuth/profile.html",
        {
            "associated_spotify_tokens": associated_spotify_tokens,
            "messages": error_message,
        },
    )


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()

        # Log the user out
        logout(request)

        return redirect("home")

    return render(request, "UserAuth/delete_account.html")


def delete_token(request):
    if request.method == "POST":
        spotify_account_username = request.POST.get("spotify_account_username")
        SpotifyToken.objects.filter(
            spotify_account_username=spotify_account_username
        ).delete()

    return redirect("profile")


def logout_view(request):
    logout(request)
    return redirect("home")


def callback(request):
    code = request.GET.get("code")

    try:
        response = post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        response.raise_for_status()
    except exceptions.RequestException as e:
        return redirect("/login?error=spotify_auth_failed")

    response_data = response.json()
    access_token = response_data.get("access_token")
    token_type = response_data.get("token_type")
    refresh_token = response_data.get("refresh_token")
    expires_in = response_data.get("expires_in")

    spotify_user_data = getSpotifyUserData(access_token)
    matching_existing_tokens = SpotifyToken.objects.filter(
        spotify_account_email=spotify_user_data["email"]
    )
    if not request.user.is_authenticated:
        if matching_existing_tokens.exists():
            login(request, matching_existing_tokens[0].user)
            matching_existing_tokens[0].user.default_spotify_token = (
                matching_existing_tokens[0]
            )
            matching_existing_tokens[0].user.save()
        elif User.objects.filter(username=spotify_user_data["email"]).exists():
            raise Exception(
                f"Failed to create account or Oauth with email: {spotify_user_data['email']}, either create an account with username and password and then link or log in to the an account and then link."
            )
        else:
            user = User.objects.create_user(
                username=spotify_user_data["email"])
            if user is not None:
                login(request, user)
            else:
                redirect("/login?error=an account with this email already exists")
    elif (
        matching_existing_tokens.exists()
        and matching_existing_tokens[0].user.username != request.user.username
    ):
        HttpResponseBadRequest(
            f"This spotify account has already been linked with another Wrapped account"
        )
    update_or_create_user_tokens(
        request.user,
        access_token,
        token_type,
        expires_in,
        refresh_token,
        spotify_account_email=spotify_user_data["email"],
        spotify_account_username=spotify_user_data["id"],
    )

    return redirect("home")


def getSpotifyUserData(access_token):
    """
    Retrieve Spotify user information.

    Args:
    access_token (str): Spotify API access token.

    Returns:
    dict: User information.
    """

    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to retrieve user info. Status code: {response.status_code}"
        )


@login_required
def deepcut(request):
    return redirect(request, reverse("Wrapped:deepcut"))
