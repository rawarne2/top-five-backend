from rest_framework import serializers
from .models import User as UserModel, Interest, Profile, Match


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ['id', 'first_name', 'last_name',
                  'email', 'phone_number', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True, 'required': True},
                        'first_name': {'required': True}, 'phone_number': {'required': True}}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'interests', 'picture_urls', 'birthdate',
                  'gender', 'location', 'preferred_gender', 'min_preferred_age', 'max_preferred_age']


class MatchSerializer(serializers.ModelSerializer):
    user1 = UserSerializer()
    user2 = UserSerializer()

    class Meta:
        model = Match
        fields = ['user1', 'user2', 'matched_on']
