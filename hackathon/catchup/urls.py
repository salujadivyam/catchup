from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout_view, name="logout"),
    path("friends", views.friends, name="friends"),
    path("addfriend", views.addfriend, name="addfriend"),
    path("acceptfriend", views.acceptfriend, name="acceptfriend"),
    path('get_chat/<int:friend_id>/', views.get_chat, name='get_chat'),
    path('send_message/<int:friend_id>/', views.send_message, name="send_message"),
    path('profilepage', views.profilepage, name="profilepage"),
    path('settings', views.settings, name="settings"),
    path('change_username/', views.change_username, name='change_username'),
    path("update_profile_picture/", views.update_profile_picture, name="update_profile_picture")
]