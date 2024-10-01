from rest_framework import serializers
from .models import User, Interest, Profile, Match


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'email', 'birthdate', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'first_name': {'required': True},
            'birthdate': {'required': True}
        }


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'interests', 'picture_urls', 'gender', 'location',
                  'preferred_gender', 'min_preferred_age', 'max_preferred_age', 'phone_number']


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSerializer()
    user2 = UserSerializer()

    class Meta:
        model = Match
        fields = ['user1', 'user2', 'matched_on']
