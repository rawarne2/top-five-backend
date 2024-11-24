from datetime import date
from tokenize import TokenError
from typing import List
from django.contrib.auth import logout, authenticate, login
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from botocore.exceptions import NoCredentialsError
import boto3
import logging
import re
from psycopg import IntegrityError

from topfive import settings
from users.types import DeleteUserData, LoginData, LogoutData, MatchData, MatchesResponse, PasswordChangeData, PasswordResetData, PotentialMatchesResponse, PresignedUrlsRequest, ProfileData, UserCreateData, UserUpdateData
from .serializers import UserSerializer, ProfileSerializer
from .models import Match, User, Profile
from .utils import get_user_from_db
from .choices import *

logger = logging.getLogger(__name__)

# TODO: make a views folder and separate this into files for each view
'''
User Views
'''


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request: Request) -> Response:
    user_data: UserCreateData = request.data
    try:
        user = User.objects.create_user(**user_data)
    except IntegrityError:
        return Response({'error': 'A user with that email already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
@csrf_exempt
def update_user(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user

    try:
        update_data: UserUpdateData = request.data
        serializer = UserSerializer(user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in update_user: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@csrf_exempt
def delete_user(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user

    if request.user.id != user.id and not request.user.is_staff:
        return Response({'error': 'You do not have permission to delete this account'},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        delete_data: DeleteUserData = request.data
        refresh_token = delete_data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                return Response({'error': 'Invalid or expired refresh token'},
                                status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        logout(request)
        return Response({'success': 'User deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
PROFILE
'''


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_profile(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user
    try:
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_profile for user_id {user_id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_profile(request: Request, user_id: int) -> Response:
    try:
        profile: Profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        update_data: ProfileData = request.data

        # TODO: extract into separate function
        # TODO: allow deleting pictures
        if 'picture_urls' in update_data:
            def find_photo_index(url):
                match = re.search(r'photo_(\d+)\.[^/]+$', url)
                if match:
                    return int(match.group(1))
                return None
            photo_indexes = [find_photo_index(url)
                             for url in update_data['picture_urls']]
            new_photos_to_save = profile.picture_urls
            for index, url in zip(photo_indexes, update_data['picture_urls']):
                if index >= len(new_photos_to_save):
                    new_photos_to_save.append(url)
                else:
                    new_photos_to_save[index] = url
            update_data['picture_urls'] = new_photos_to_save
        serializer = ProfileSerializer(profile, data=update_data, partial=True)

        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(
            f"Error in update_profile for user_id {user_id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
AUTHENTICATION VIEWS
'''


@ api_view(['POST'])
@ permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    try:
        data: LoginData = request.data
        user = authenticate(
            request, email=data['email'].lower(), password=data['password'])
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in login_view: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ api_view(['POST'])
@ permission_classes([IsAuthenticated])
def logout_view(request: Request) -> Response:
    try:
        data: LogoutData = request.data
        refresh_token = data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'success': 'User logged out successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    except TokenError:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in logout_view: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ api_view(['POST'])
@ permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    try:
        data: PasswordChangeData = request.data
        user = request.user
        if user.check_password(data['old_password']):
            user.set_password(data['new_password'])
            user.save()
            return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Incorrect old password'}, status=status.HTTP_400_BAD_REQUEST)
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(
            f"Error in change_password for user {request.user.id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ api_view(['POST'])
@ permission_classes([AllowAny])
def reset_password(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user
    try:
        data: PasswordResetData = request.data
        user.set_password(data['new_password'])
        user.save()
        return Response({'success': 'Password reset successfully'}, status=status.HTTP_200_OK)
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in reset_password for user {user_id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
Matches VIEWS
'''


def user_to_match_data(user: User) -> MatchData:
    return {
        'id': user.id,
        'first_name': user.first_name,
        'picture_url': user.profile.picture_urls[0] if user.profile.picture_urls else None
    }


@ api_view(['GET'])
@ permission_classes([IsAuthenticated])
def get_potential_matches(request: Request) -> Response:
    try:
        user_profile = request.user.profile
        min_age = user_profile.min_preferred_age
        max_age = user_profile.max_preferred_age
        preferred_gender = user_profile.preferred_gender

        today = date.today()
        min_birth_date = date(today.year - max_age, today.month, today.day)
        max_birth_date = date(today.year - min_age, today.month, today.day)

        potential_matches = User.objects.filter(
            profile__gender=preferred_gender,
            birthdate__gte=min_birth_date,
            birthdate__lte=max_birth_date
        ).exclude(id=request.user.id)

        # Exclude users who are already matches
        existing_matches = Match.objects.filter(Q(user1=request.user) | Q(
            user2=request.user)).values_list('user1', 'user2')
        existing_match_ids = set(
            [user_id for match in existing_matches for user_id in match if user_id != request.user.id])
        potential_matches = potential_matches.exclude(
            id__in=existing_match_ids)

        response_data: PotentialMatchesResponse = {
            'potential_matches': [user_to_match_data(user) for user in potential_matches]
        }
        return Response(response_data)
    except Exception as e:
        logger.error(
            f"Error in get_potential_matches for user {request.user.id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ api_view(['GET'])
@ permission_classes([IsAuthenticated])
def get_matches(request: Request) -> Response:
    try:
        user_matches = Match.objects.filter(
            Q(user1=request.user) | Q(user2=request.user))
        matched_users = []
        for match in user_matches:
            matched_user = match.user2 if match.user1 == request.user else match.user1
            matched_users.append(matched_user)

        response_data: MatchesResponse = {
            'matches': [user_to_match_data(user) for user in matched_users]
        }
        return Response(response_data)
    except Exception as e:
        logger.error(
            f"Error in get_matches for user {request.user.id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
OTHER VIEWS
'''

# TODO: cleanup old photos when new ones are added
# TODO: use this as a function in update profile view instead of having a separate view and making multiple calls


@ api_view(['PUT'])
@ permission_classes([IsAuthenticated])
def get_presigned_urls(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user

    try:
        data: PresignedUrlsRequest = request.data
        photo_indexes: List[int] = data.get('photo_indexes')

        if not photo_indexes:
            return Response({'error': 'No photo indexes provided'}, status=status.HTTP_400_BAD_REQUEST)
        if len(photo_indexes) > 6:
            return Response({'error': 'This operation would exceed the maximum of 6 photos.'},
                            status=status.HTTP_400_BAD_REQUEST)

        s3_client = boto3.client('s3',
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                 region_name=settings.AWS_S3_REGION_NAME)

        presigned_urls: List[str] = []
        for i in photo_indexes:
            key = f'user_{user_id}/photo_{i}.jpg'
            presigned_url = s3_client.generate_presigned_url('put_object',
                                                             Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                     'Key': key},
                                                             ExpiresIn=3600)
            presigned_urls.append(presigned_url)

        response = {'presigned_urls': presigned_urls}
        return Response(response)

    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return Response({'error': 'AWS credentials not available'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(
            f"Error in get_presigned_urls for user_id {user_id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@ permission_classes([AllowAny])
@api_view(['GET'])
def get_profile_choices(request):
    """Return all choice options for profile fields"""
    return Response({
        'alcohol': [{'value': v, 'label': l} for v, l in ALCOHOL_CHOICES],
        'body_type': [{'value': v, 'label': l} for v, l in BODY_TYPE_CHOICES],
        'cannabis': [{'value': v, 'label': l} for v, l in CANNABIS_CHOICES],
        'communication_style': [{'value': v, 'label': l} for v, l in COMMUNICATION_STYLE_CHOICES],
        'diet': [{'value': v, 'label': l} for v, l in DIET_CHOICES],
        'education': [{'value': v, 'label': l} for v, l in EDUCATION_CHOICES],
        'ethnicity': [{'value': v, 'label': l} for v, l in ETHNICITY_CHOICES],
        'exercise': [{'value': v, 'label': l} for v, l in EXERCISE_CHOICES],
        'gender': [{'value': v, 'label': l} for v, l in GENDER_CHOICES],
        'interests': [{'value': v, 'label': l} for v, l in INTEREST_CHOICES],
        'love_languages': [{'value': v, 'label': l} for v, l in LOVE_LANGUAGE_CHOICES],
        'personality_type': [{'value': v, 'label': l} for v, l in PERSONALITY_TYPE_CHOICES],
        'pets': [{'value': v, 'label': l} for v, l in PET_CHOICES],
        'political': [{'value': v, 'label': l} for v, l in POLITICAL_CHOICES],
        'pronouns': [{'value': v, 'label': l} for v, l in PRONOUN_CHOICES],
        'relationship_goals': [{'value': v, 'label': l} for v, l in RELATIONSHIP_GOAL_CHOICES],
        'religion': [{'value': v, 'label': l} for v, l in RELIGION_CHOICES],
        'sexual_orientation': [{'value': v, 'label': l} for v, l in SEXUAL_ORIENTATION_CHOICES],
        'sleep_pattern': [{'value': v, 'label': l} for v, l in SLEEP_PATTERN_CHOICES],
        'social_media_usage': [{'value': v, 'label': l} for v, l in SOCIAL_MEDIA_USAGE_CHOICES],
        'vaccine_status': [{'value': v, 'label': l} for v, l in VACCINE_STATUS_CHOICES],
        'zodiac': [{'value': v, 'label': l} for v, l in ZODIAC_CHOICES]
    })
