from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.forms import ValidationError
from datetime import datetime, timedelta


class Interest(models.Model):
    name = models.CharField(max_length=25, unique=True)
    # TODO: make a list of common interest choices


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
    picture_urls = ArrayField(models.TextField(), blank=True, default=list,)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    preferred_gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    min_preferred_age = models.IntegerField(default=18)
    max_preferred_age = models.IntegerField(default=99)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    height = models.PositiveIntegerField(
        blank=True, null=True)  # Height in centimeters
    PRONOUN_CHOICES = [
        ('he/him', 'He/Him'),
        ('she/her', 'She/Her'),
        ('they/them', 'They/Them'),
        ('other', 'Other'),
    ]
    pronouns = models.CharField(
        max_length=10, choices=PRONOUN_CHOICES, blank=True, null=True)
    EDUCATION_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    highest_education = models.CharField(
        max_length=15, choices=EDUCATION_CHOICES, blank=True, null=True)
    POLITICAL_CHOICES = [
        ('liberal', 'Liberal'),
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('apolitical', 'Apolitical'),
        ('other', 'Other'),
    ]
    political_views = models.CharField(
        max_length=15, choices=POLITICAL_CHOICES, blank=True, null=True)
    PET_CHOICES = [
        ('dogs', 'Dogs'),
        ('cats', 'Cats'),
        ('birds', 'Birds'),
        ('reptiles', 'Reptiles'),
        ('small_animals', 'Small Animals'),
        ('multiple', 'Multiple Types'),
        ('none', 'None'),
    ]
    pet_preferences = models.CharField(
        max_length=15, choices=PET_CHOICES, default='none')
    EXERCISE_CHOICES = [
        ('never', 'Never'),
        ('rarely', 'Rarely'),
        ('sometimes', 'Sometimes'),
        ('often', 'Often'),
        ('daily', 'Daily'),
    ]
    exercise_level = models.CharField(
        max_length=10, choices=EXERCISE_CHOICES, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    goals = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    objects = models.Manager()

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

    def clean(self):
        # Ensure the number of picture_urls is between 1 and 6
        if not (1 <= len(self.picture_urls) <= 6):
            raise ValidationError(
                'Users must have between 1 and 6 picture_urls.')
        if self.picture_urls:
            current_time = int(datetime.now().timestamp())
            self.picture_urls = [
                f"{url.split('?')[0]}?t={current_time}"
                for url in self.picture_urls
            ]

    def save(self, *args, **kwargs):
        # Call the full clean method to perform validation
        self.full_clean()
        super().save(*args, **kwargs)


class Match(models.Model):
    user1 = models.ForeignKey(
        User, related_name='match1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, related_name='match2', on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)
