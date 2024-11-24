from django.contrib import admin
from .models import User, Profile, Prompt, PromptResponse, Match


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'date_joined', 'last_login')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'location',
                    'relationship_goals', 'religion')
    list_filter = (
        'gender',
        'relationship_goals',
        'religion',
        'sexual_orientation',
        'exercise_level',
        'highest_education'
    )
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'location'
    )
    raw_id_fields = ('user',)


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('text',)


@admin.register(PromptResponse)
class PromptResponseAdmin(admin.ModelAdmin):
    list_display = ('profile', 'prompt', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('profile__user__email', 'prompt__text', 'response')
    raw_id_fields = ('profile', 'prompt')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'matched_at')
    list_filter = ('matched_at',)
    search_fields = (
        'user1__email',
        'user1__first_name',
        'user2__email',
        'user2__first_name'
    )
    raw_id_fields = ('user1', 'user2')
