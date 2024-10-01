from datetime import date
from tokenize import TokenError
from typing import Dict, List, Tuple
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
from psycopg import IntegrityError

from topfive import settings
from users.types import DeleteUserData, LoginData, LogoutData, MatchData, MatchesResponse, PasswordChangeData, PasswordResetData, PotentialMatchesResponse, PresignedUrl, PresignedUrlsRequest, PresignedUrlsResponse, ProfileUpdateData, UserCreateData, UserUpdateData
from .serializers import UserSerializer, ProfileSerializer
from .models import Match, User, Profile
from .utils import get_user_from_db


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


PictureURL = Tuple[int, str]


def update_picture_urls(existing_urls: List[PictureURL], new_picture_urls: List[PictureURL]) -> List[PictureURL]:
    # Convert existing_urls to a dictionary for easier manipulation
    url_dict: Dict[int, str] = {
        int(index): url for index, url in existing_urls}

    # Update with new URLs
    for index, url in new_picture_urls:
        if 0 <= index < 7:
            url_dict[index] = url

    # Convert back to list of tuples and sort by index
    updated_urls = list(url_dict.items())
    updated_urls.sort(key=lambda x: x[0])

    return updated_urls[:7]  # Ensure we don't exceed 7 photos


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_profile(request: Request, user_id: int) -> Response:
    try:
        profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        update_data = request.data
        old_picture_urls = profile.picture_urls.copy()

        # Handle picture_urls separately
        if 'picture_urls' in update_data:
            # Convert the incoming data to the correct format
            new_picture_urls = []
            for item in update_data['picture_urls']:
                if isinstance(item, dict) and 'index' in item and 'url' in item:
                    try:
                        index = int(item['index'])
                        new_picture_urls.append((index, item['url']))
                    except ValueError:
                        # If index can't be converted to int, skip this entry
                        continue
                elif isinstance(item, (list, tuple)) and len(item) == 2:
                    try:
                        index = int(item[0])
                        new_picture_urls.append((index, item[1]))
                    except ValueError:
                        # If index can't be converted to int, skip this entry
                        continue

            new_picture_urls = update_picture_urls(
                profile.picture_urls, new_picture_urls)
            update_data['picture_urls'] = new_picture_urls

        serializer = ProfileSerializer(profile, data=update_data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()

            # Clean up S3 after successful database update
            if 'picture_urls' in update_data:
                cleanup_s3_photos(user_id, old_picture_urls, new_picture_urls)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(
            f"Error in update_profile for user_id {user_id}: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def cleanup_s3_photos(user_id: int, old_urls: List[PictureURL], new_urls: List[PictureURL]):
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_S3_REGION_NAME)

    old_dict = dict(old_urls)
    new_dict = dict(new_urls)

    for index, old_url in old_dict.items():
        if old_url and (index not in new_dict or new_dict[index] != old_url):
            old_key = f'user_{user_id}/photo_{index}.jpg'
            try:
                s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_key)
                logger.info(
                    f"Deleted old photo for user {user_id} at index {index}")
            except Exception as e:
                logger.error(
                    f"Failed to delete old photo for user {user_id} at index {index}: {str(e)}")


'''
AUTHENTICATION VIEWS
'''


@api_view(['POST'])
@permission_classes([AllowAny])
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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


@api_view(['POST'])
@permission_classes([AllowAny])
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def get_presigned_urls(request: Request, user_id: int) -> Response:
    user = get_user_from_db(user_id)
    if isinstance(user, Response):
        return user

    try:
        data: PresignedUrlsRequest = request.data
        photo_count = data.get('photo_count', 0)

        if photo_count <= 0:
            return Response({'error': 'Invalid photo count'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            profile = Profile.objects.select_for_update().get(user_id=user_id)

            # Count existing non-null photos
            existing_photos = sum(
                1 for url in profile.picture_urls if url is not None)

            # Check if this operation would exceed the 7-photo limit
            if existing_photos + photo_count > 7:
                return Response({'error': 'This operation would exceed the maximum of 7 photos.'},
                                status=status.HTTP_400_BAD_REQUEST)

            s3_client = boto3.client('s3',
                                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                     region_name=settings.AWS_S3_REGION_NAME)

            presigned_urls: List[PresignedUrl] = []

            for i in range(photo_count):
                # Find the next available index
                next_index = next((i for i, url in enumerate(
                    profile.picture_urls) if url is None), len(profile.picture_urls))
                if next_index >= 7:
                    # This shouldn't happen due to the earlier check, but just in case
                    return Response({'error': 'No available slots for new photos'}, status=status.HTTP_400_BAD_REQUEST)

                key = f'user_{user_id}/photo_{next_index}.jpg'
                presigned_url = s3_client.generate_presigned_url('put_object',
                                                                 Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                         'Key': key},
                                                                 ExpiresIn=3600)
                presigned_urls.append({
                    'index': next_index,
                    'url': presigned_url
                })

        response: PresignedUrlsResponse = {'presigned_urls': presigned_urls}
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
