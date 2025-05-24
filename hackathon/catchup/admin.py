from django.contrib import admin
from .models import Message, UserProfile, FriendRequest

# Register your models here.
admin.site.register(Message)
admin.site.register(UserProfile)
admin.site.register(FriendRequest)