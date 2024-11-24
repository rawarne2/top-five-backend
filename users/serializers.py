from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Prompt, PromptResponse, Match
from .choices import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name',
                  'last_name', 'birthdate', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'required': True},
            'birthdate': {'required': True}
        }


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'text', 'is_active']


class PromptResponseSerializer(serializers.ModelSerializer):
    prompt_text = serializers.CharField(source='prompt.text', read_only=True)

    class Meta:
        model = PromptResponse
        fields = ['id', 'prompt', 'prompt_text',
                  'response', 'created_at', 'updated_at']


class ProfileSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    prompt_responses = PromptResponseSerializer(
        many=True, read_only=True, source='promptresponse_set'
    )

    # Field display values
    alcohol_frequency_display = serializers.CharField(
        source='get_alcohol_frequency_display', read_only=True)
    body_type_display = serializers.CharField(
        source='get_body_type_display', read_only=True)
    cannabis_friendly_display = serializers.CharField(
        source='get_cannabis_friendly_display', read_only=True)
    communication_style_display = serializers.CharField(
        source='get_communication_style_display', read_only=True)
    dietary_preferences_display = serializers.CharField(
        source='get_dietary_preferences_display', read_only=True)
    ethnicity_display = serializers.CharField(
        source='get_ethnicity_display', read_only=True)
    exercise_level_display = serializers.CharField(
        source='get_exercise_level_display', read_only=True)
    gender_display = serializers.CharField(
        source='get_gender_display', read_only=True)
    highest_education_display = serializers.CharField(
        source='get_highest_education_display', read_only=True)
    personality_type_display = serializers.CharField(
        source='get_personality_type_display', read_only=True)
    pet_preferences_display = serializers.CharField(
        source='get_pet_preferences_display', read_only=True)
    political_views_display = serializers.CharField(
        source='get_political_views_display', read_only=True)
    preferred_gender_display = serializers.CharField(
        source='get_preferred_gender_display', read_only=True)
    relationship_goals_display = serializers.CharField(
        source='get_relationship_goals_display', read_only=True)
    religion_display = serializers.CharField(
        source='get_religion_display', read_only=True)
    sexual_orientation_display = serializers.CharField(
        source='get_sexual_orientation_display', read_only=True)
    sleep_pattern_display = serializers.CharField(
        source='get_sleep_pattern_display', read_only=True)
    social_media_usage_display = serializers.CharField(
        source='get_social_media_usage_display', read_only=True)
    vaccine_status_display = serializers.CharField(
        source='get_covid_vaccine_status_display', read_only=True)
    zodiac_sign_display = serializers.CharField(
        source='get_zodiac_sign_display', read_only=True)

    # Handle ArrayFields with choices
    interests_display = serializers.SerializerMethodField()
    love_languages_display = serializers.SerializerMethodField()
    pronouns_display = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'user_details',
            # Basic Info
            'bio',
            'ethnicity',
            'ethnicity_display',
            'gender',
            'gender_display',
            'height',
            'location',
            'pronouns',
            'pronouns_display',
            'sexual_orientation',
            'sexual_orientation_display',
            'zodiac_sign',
            'zodiac_sign_display',
            # Contact & Social
            'communication_style',
            'communication_style_display',
            'phone_number',
            'social_media_usage',
            'social_media_usage_display',
            # Education & Work
            'company',
            'highest_education',
            'highest_education_display',
            'job_title',
            # Lifestyle
            'alcohol_frequency',
            'alcohol_frequency_display',
            'cannabis_friendly',
            'cannabis_friendly_display',
            'covid_vaccine_status',
            'vaccine_status_display',
            'dietary_preferences',
            'dietary_preferences_display',
            'exercise_level',
            'exercise_level_display',
            'pet_preferences',
            'pet_preferences_display',
            'political_views',
            'political_views_display',
            'religion',
            'religion_display',
            'sleep_pattern',
            'sleep_pattern_display',
            # Personality & Values
            'body_type',
            'body_type_display',
            'family_plans',
            'interests',
            'interests_display',
            'life_goals',
            'love_languages',
            'love_languages_display',
            'personality_type',
            'personality_type_display',
            'relationship_goals',
            'relationship_goals_display',
            'special_talents',
            # Photos
            'picture_urls',
            # Preferences
            'max_preferred_age',
            'min_preferred_age',
            'preferred_gender',
            'preferred_gender_display',
            # Prompts
            'prompts',
            'prompt_responses'
        ]

    def get_interests_display(self, obj):
        """Return display names for interests"""
        return [
            dict(INTEREST_CHOICES).get(interest)
            for interest in obj.interests
        ] if obj.interests else []

    def get_love_languages_display(self, obj):
        """Return display names for love languages"""
        return [
            dict(LOVE_LANGUAGE_CHOICES).get(lang)
            for lang in obj.love_languages
        ] if obj.love_languages else []

    def get_pronouns_display(self, obj):
        """Return display names for pronouns"""
        return [
            dict(PRONOUN_CHOICES).get(pronoun)
            for pronoun in obj.pronouns
        ] if obj.pronouns else []


class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    user1_profile = ProfileSerializer(source='user1.profile', read_only=True)
    user2_profile = ProfileSerializer(source='user2.profile', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id',
            'user1',
            'user2',
            'user1_profile',
            'user2_profile',
            'matched_at'
        ]
