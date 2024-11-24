from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.forms import ValidationError
from datetime import datetime, timedelta
from .choices import *


class Prompt(models.Model):
    is_active = models.BooleanField(default=True)
    text = models.CharField(max_length=250)

    def __str__(self):
        return self.text


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        Profile.objects.create(user=user)
        return user


class User(AbstractUser, PermissionsMixin):
    birthdate = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'birthdate']

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()


class Profile(models.Model):
    alcohol_frequency = models.CharField(
        max_length=20, choices=ALCOHOL_CHOICES, default='prefer_not_to_say')
    bio = models.TextField(blank=True)
    body_type = models.CharField(
        max_length=20, choices=BODY_TYPE_CHOICES, default='prefer_not_to_say')
    cannabis_friendly = models.CharField(
        max_length=20, choices=CANNABIS_CHOICES, default='prefer_not_to_say')
    communication_style = models.CharField(
        max_length=15, choices=COMMUNICATION_STYLE_CHOICES, default='mixed')
    company = models.CharField(max_length=100, blank=True, null=True)
    covid_vaccine_status = models.CharField(
        max_length=20, choices=VACCINE_STATUS_CHOICES, default='prefer_not_to_say')
    dietary_preferences = models.CharField(
        max_length=15, choices=DIET_CHOICES, default='omnivore')
    family_plans = models.CharField(
        max_length=40, choices=FAMILY_PLANS, default='undecided')
    ethnicity = models.CharField(
        max_length=20, choices=ETHNICITY_CHOICES, default='prefer_not_to_say')
    exercise_level = models.CharField(
        max_length=10, choices=EXERCISE_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.PositiveIntegerField(blank=True, null=True)
    highest_education = models.CharField(
        max_length=18, choices=EDUCATION_CHOICES, blank=True, null=True)
    interests = ArrayField(
        models.CharField(max_length=20, choices=INTEREST_CHOICES),
        blank=True,
        default=list
    )
    job_title = models.CharField(max_length=100, blank=True, null=True)
    life_goals = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100)
    love_languages = ArrayField(
        models.CharField(max_length=20, choices=LOVE_LANGUAGE_CHOICES),
        blank=True,
        default=list
    )
    max_preferred_age = models.IntegerField(default=99)
    min_preferred_age = models.IntegerField(default=18)
    personality_type = models.CharField(
        max_length=10, choices=PERSONALITY_TYPE_CHOICES, default='unknown')
    pet_preferences = models.CharField(
        max_length=15, choices=PET_CHOICES, default='none')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    picture_urls = ArrayField(models.TextField(), blank=True, default=list)
    political_views = models.CharField(
        max_length=12, choices=POLITICAL_CHOICES, blank=True, null=True)
    preferred_gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    prompts = models.ManyToManyField('Prompt', through='PromptResponse')
    pronouns = ArrayField(
        models.CharField(max_length=20, choices=PRONOUN_CHOICES),
        blank=True,
        default=list,
        help_text="User's preferred pronouns (can select multiple)"
    )
    relationship_goals = models.CharField(
        max_length=20, choices=RELATIONSHIP_GOAL_CHOICES, default='not_sure')
    religion = models.CharField(
        max_length=20, choices=RELIGION_CHOICES, default='prefer_not_to_say')
    sexual_orientation = models.CharField(
        max_length=20, choices=SEXUAL_ORIENTATION_CHOICES, default='prefer_not_to_say')
    sleep_pattern = models.CharField(
        max_length=15, choices=SLEEP_PATTERN_CHOICES, default='regular')
    social_media_usage = models.CharField(
        max_length=15, choices=SOCIAL_MEDIA_USAGE_CHOICES, default='moderate')
    special_talents = models.TextField(blank=True, null=True)
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='profile')
    zodiac_sign = models.CharField(
        max_length=15, choices=ZODIAC_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def clean(self):
        if not (1 <= len(self.picture_urls) <= 6):
            raise ValidationError(
                'Users must have between 1 and 6 picture_urls.')
        if self.picture_urls:
            current_time = int(datetime.now().timestamp())
            self.picture_urls = [
                f"{url.split('?')[0]}?t={current_time}"
                for url in self.picture_urls
            ]

        if self.pronouns and not all(pronoun in dict(PRONOUN_CHOICES) for pronoun in self.pronouns):
            raise ValidationError('Invalid pronoun choice provided')

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PromptResponse(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'prompt'],
                name='unique_profile_prompt'
            )
        ]


class Match(models.Model):
    user1 = models.ForeignKey(
        User, related_name='match1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, related_name='match2', on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)
