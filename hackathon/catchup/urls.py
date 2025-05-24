from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout_view, name="logout"),
    path("friends", views.friends, name="friends"),
    path("chatroom/<int:id>", views.chatroom, name="chatroom"),
]