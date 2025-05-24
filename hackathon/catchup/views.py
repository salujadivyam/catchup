import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import User, Message, UserProfile, FriendRequest

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user = request.user
        friends = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            accepted=True
        )
        friend_users = []
        for fr in friends:
            friend_users.append(fr.to_user if fr.from_user == user else fr.from_user)


        return render(request, "catchup/chat_page_dark.html", {
            "user": user.username,
            "friends": friend_users
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "catchup/login.html", {
                "login_message": "Invalid email and/or password."
            })
    else:
        return render(request, "catchup/login.html")
    
def signup(request):
    if request.method == "POST":
        gmail = request.POST["gmail"]
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "catchup/login.html", {
                "message": "Username already taken."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, email=gmail, password=password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "catchup/login.html", {
                "signup_message": "An error occurred. Please try again."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def chatroom(request, id):

    return 

def friends(request):
    user = request.user
    friends = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            accepted=True
        )
    friend_users = []
    for fr in friends:
        friend_users.append(fr.to_user if fr.from_user == user else fr.from_user)

    friendreqs = FriendRequest.objects.filter(
                Q(from_user=user) | Q(to_user=user),
                accepted=False
            )
    friendreq_users = []
    for fr in friendreqs:
        friendreq_users.append(fr.to_user if fr.from_user == user else fr.from_user)
    return render(request, 'catchup/friendrequests.html', {
        "friends": friend_users,
        "friendreqs": friendreq_users
    })

def addfriend(request):
    return