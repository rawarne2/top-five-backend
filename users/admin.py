from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class UserProfileAdmin(UserAdmin):
    model = UserProfile


# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
