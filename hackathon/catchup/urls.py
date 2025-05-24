from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout_view, name="logout"),
    path("friends", views.friends, name="friends"),
    path("addfriend", views.addfriend, name="addfriend"),
    path("chatroom/<int:id>", views.chatroom, name="chatroom"),
    path("acceptfriend", views.acceptfriend, name="acceptfriend"),
    path('get_chat/<int:friend_id>/', views.get_chat, name='get_chat'),
]