from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    gender_options = [("male", "Male"), ("female", "Female"),
                      ("non-binary", "Non-Binary")]
    bio = models.TextField(max_length=500)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=gender_options)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=100)

    # Matching preferences
    preferred_age_max = models.PositiveIntegerField(default=100)
    preferred_age_min = models.PositiveIntegerField(default=18)
    preferred_gender = models.CharField(max_length=10, choices=gender_options)

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'birthdate']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return str(self.email)
