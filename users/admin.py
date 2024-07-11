from django.contrib import admin
from .models import User, Profile, Interest, Match


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_joined', 'last_login', 'profile')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('gender', 'location', 'preferred_gender',
                    'min_preferred_age', 'max_preferred_age')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'matched_at')
