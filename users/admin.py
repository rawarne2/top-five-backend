from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # what gets displayed in django admin
    list_display = ("first_name", "age", "email")
    model = CustomUser


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
