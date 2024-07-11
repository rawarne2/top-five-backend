from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from datetime import datetime, timedelta


class Interest(models.Model):
    name = models.CharField(max_length=25, unique=True)


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    def __str__(self):
        return self.get_full_name()


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-Binary'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField()
    interests = models.ManyToManyField(Interest, blank=True)
    picture_urls = models.URLField(null=True, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    preferred_gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    min_preferred_age = models.IntegerField(default=18)
    max_preferred_age = models.IntegerField(default=99)

    objects = models.Manager()

    # TODO:
    def get_filtered_profiles(self):
        if self.preferred_gender:
            today = datetime.now().date()
            min_birthdate = today - \
                timedelta(days=self.max_preferred_age * 365)
            max_birthdate = today - \
                timedelta(days=self.min_preferred_age * 365)
            potential_matches = Profile.objects.filter(
                gender=self.preferred_gender,
                birthdate__range=(min_birthdate, max_birthdate)
            )
            return potential_matches
        return Profile.objects.none()


class Match(models.Model):
    user1 = models.ForeignKey(
        User, related_name='match1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, related_name='match2', on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)
