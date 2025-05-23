import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import User

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "catchup/chat_page_dark.html")
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