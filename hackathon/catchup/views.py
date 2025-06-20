import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import User, Message, UserProfile, FriendRequest
from django.utils.timezone import localtime

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user = request.user
        friend_data = get_friend_data(user)
        return render(request, "catchup/chat_page_dark.html", {
            "user": user,
            "friends": friend_data
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

def friends(request):
    user = request.user

    # Get all pending requests sent TO the current user
    friend_requests = FriendRequest.objects.filter(to_user=user, accepted=False)

    # Get all accepted friends (optional, if you also display the friend list)
    friends = FriendRequest.objects.filter(
        Q(from_user=user) | Q(to_user=user),
        accepted=True
    )
    friend_users = [fr.to_user if fr.from_user == user else fr.from_user for fr in friends]

    return render(request, "catchup/friendrequests.html", {
        "friendreqs": friend_requests,
        "friends": get_friend_data(request.user),
        "friendusers": friend_users
    })

def addfriend(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if not username:
            return JsonResponse({"success": False, "error": "Username is required."})

        try:
            to_user = User.objects.get(username=username)
            from_user = request.user

            if to_user == from_user:
                return JsonResponse({"success": False, "error": "You cannot send a friend request to yourself."})

            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                return JsonResponse({"success": False, "error": "Friend request already sent."})

            FriendRequest.objects.create(from_user=from_user, to_user=to_user)
            return JsonResponse({"success": True, "message": "Friend request sent."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found."})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
def acceptfriend(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

        friend_request.accepted = True
        friend_request.save()

        return JsonResponse({"success": True, "message": "Friend request accepted."})
    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required
def get_chat(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    messages = Message.objects.filter(
        sender__in=[request.user, friend],
        receiver__in=[request.user, friend]
    ).order_by("timestamp")

    Message.objects.filter(sender=friend, receiver=request.user, is_read=False).update(is_read=True)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "catchup/chatroom_partial.html", {
            "messages": messages,
            "friend": friend,
        })
    else:
        return render(request, "catchup/chat_page_dark.html", {
            "messages": messages,
            "friend": friend,
        })

@login_required
def send_message(request, friend_id):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            receiver = get_object_or_404(User, id=friend_id)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )

    # After sending, reload the chat page with messages
    friend = get_object_or_404(User, id=friend_id)
    messages = Message.objects.filter(
        sender__in=[request.user, friend],
        receiver__in=[request.user, friend]
    ).order_by("timestamp")

    user = request.user
    friends = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            accepted=True
        )
    friend_users = []
    for fr in friends:
        friend_users.append(fr.to_user if fr.from_user == user else fr.from_user)

    return render(request, "catchup/chat_page_dark.html", {
        "messages": messages,
        "friend": friend,
        "friends": get_friend_data(request.user),
        "user": request.user,
    })

def profilepage(request):
    user = request.user
    return render(request, 'catchup/profile.html', {
        "user": user,
        "friends": get_friend_data(request.user)
    })

def settings(request):
    return render(request, 'catchup/settings.html', {
        "friends": get_friend_data(request.user)
    })

def get_friend_data(user):
    friends = FriendRequest.objects.filter(
        Q(from_user=user) | Q(to_user=user),
        accepted=True
    )
    data = []
    for fr in friends:
        friend = fr.to_user if fr.from_user == user else fr.from_user

        last_msg = Message.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
        ).order_by("-timestamp").first()

        profile = UserProfile.objects.filter(user=friend).first()

        has_unread = Message.objects.filter(
            sender=friend,
            receiver=user,
            is_read=False
        ).exists()

        data.append({
            "friend": friend,
            "last_message": last_msg,
            "has_unread": has_unread,
            "profile_picture": profile.profile_picture if profile else "https://example.com/default.jpg"
        })
    return data

@login_required
def change_username(request):
    if request.method == "POST":
        new_username = request.POST.get("username")

        if not new_username:
            return render(request, "catchup/change_username.html", {
                "error": "Username cannot be empty.",
                "friends": get_friend_data(request.user)
            })

        if User.objects.filter(username=new_username).exists():
            return render(request, "catchup/change_username.html", {
                "error": "Username already taken.",
                "friends": get_friend_data(request.user)
            })

        try:
            request.user.username = new_username
            request.user.save()
            return redirect("index")  # or wherever you want
        except IntegrityError:
            return render(request, "catchup/change_username.html", {
                "error": "An error occurred. Please try again.",
                "friends": get_friend_data(request.user)
            })

    return render(request, "catchup/change_username.html", {
        "friends": get_friend_data(request.user)
    })

@login_required
def update_profile_picture(request):
    if request.method == "POST":
        image_url = request.POST.get("image_url")

        if not image_url:
            return render(request, "catchup/update_picture.html", {
                "error": "Please enter a valid image URL.",
                "friends": get_friend_data(request.user)
            })

        profile = request.user.userprofile
        profile.profile_picture = image_url
        profile.save()

        return redirect("index")

    return render(request, "catchup/update_picture.html", {
        "friends": get_friend_data(request.user)
    })
