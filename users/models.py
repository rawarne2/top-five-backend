from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.forms import ValidationError
from datetime import datetime, timedelta


class Interest(models.Model):
    name = models.CharField(max_length=25, unique=True)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        This also creates a profile for the user with default values.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        Profile.objects.create(user=user)

        return user


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    birthdate = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'birthdate']

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()


def validate_picture_urls(value):
    if len(value) > 7:
        raise ValidationError('Maximum 7 photos allowed.')
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise ValidationError('Each item must be a list of two elements.')
        if not isinstance(item[0], int) or not (0 <= item[0] <= 6):
            raise ValidationError(
                'First element must be an integer between 0 and 6.')
        if not isinstance(item[1], str):
            raise ValidationError('Second element must be a string URL.')


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-Binary'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    interests = models.ManyToManyField(Interest, blank=True)
    picture_urls = ArrayField(
        ArrayField(models.CharField(max_length=500), size=2),
        default=list,
        blank=True
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    preferred_gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    min_preferred_age = models.IntegerField(default=18)
    max_preferred_age = models.IntegerField(default=99)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

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
