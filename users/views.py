from tokenize import TokenError
from django.contrib.auth import logout, authenticate, login
from django.forms import ValidationError
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from psycopg import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .serializers import UserSerializer, ProfileSerializer
from .models import User, Profile


'''
User Views
'''


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_user(request, user_id):
    try:  # Django Debug IP in vscode to debug on device
        user = User.objects.get(id=user_id)
        if user is not None and user.is_authenticated:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'get_user error': 'Invalid user id or authentication'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        print(f"Error with token: {str(err)}")
        return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@csrf_exempt
def update_user(request, user_id):
    phone_number = request.data.get('phone_number')
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user, data=phone_number)
    if serializer.is_valid():
        serializer.update(
            user,
            serializer.validated_data
        )
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['DELETE'])
@csrf_exempt
def delete_user(request, user_id):
    token_string = request.data.get('refresh_token')

    try:
        user = User.objects.get(id=user_id)
        refresh_token = RefreshToken(token_string)
        refresh_token.blacklist()

        logout(request)
        user.delete()

        return Response({'success': 'User deleted successfully'})
    except TokenError:
        return Response({'error': 'Invalid or expired refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        return Response({'delete_user error': str(err)}, status=status.HTTP_400_BAD_REQUEST)


'''
PROFILE
'''


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_profile(request, user_id):
    try:
        profile = Profile.objects.get(user_id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as err:
        return Response({'get_user error': str(err)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def create_or_update_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        try:
            if request.method == 'POST':
                with transaction.atomic():
                    serializer.save(user=user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            if request.method == 'PUT':
                with transaction.atomic():
                    serializer.update(user.profile, serializer.validated_data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({'Profile already exists': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Create Profile error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
AUTHENTICATION VIEWS
'''


@api_view(['POST'])
@cache_control(no_cache=True)
@permission_classes([AllowAny])
@authentication_classes([JWTAuthentication])
@csrf_exempt
def login_view(request):
    password = request.data.get('password')
    email = request.data.get('email').lower()

    user_object = authenticate(request, email=email, password=password)

    if user_object:
        try:
            login(request, user_object)
            serializer = UserSerializer(user_object)
            user_data = serializer.data
            refresh_token = RefreshToken.for_user(user_object)
            access_token = refresh_token.access_token

            tokens = {
                'access': str(access_token),
                'refresh': str(refresh_token)
            }

            return Response({'user': user_data, 'tokens': tokens})
        except TokenError as err:
            return Response({'TokenError': f'Error creating token {str(err)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def logout_view(request):
    token_string = request.data.get('refresh_token')
    if token_string:
        try:
            refresh_token = RefreshToken(token_string)
            refresh_token.blacklist()

            logout(request)

            return Response({'success': 'logout was successful!'}, status=200)
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response(str(err), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'error': 'No refresh token provided.'}, status=status.HTTP_400_BAD_REQUEST)


# Create User
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request: Request) -> Response:
    try:
        request.data['username'] = request.data.get('email').lower()
        user = UserSerializer(data=request.data)
        if user.is_valid():
            new_user = User.objects.create_user(**request.data)
            login(request, new_user)
            refresh_token = RefreshToken.for_user(new_user)
            access_token = refresh_token.access_token

            tokens = {
                'access': str(access_token),
                'refresh': str(refresh_token)
            }
            return Response({'user': user.data, 'tokens': tokens}, status=status.HTTP_201_CREATED)
        else:
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as err:
        return Response({'error': f'User with that email already exists {str(err)}'}, status=status.HTTP_400_BAD_REQUEST)
    except TokenError as err:
        return Response({'TokenError': f'Error creating token {str(err)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        return Response({'signup error: ': str(err)})


# user wants to change password voluntarily and knows the old password
@api_view(['POST'])
@csrf_exempt
def change_password(request, user_id):
    user = User.objects.get(id=user_id)
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if user.check_password(old_password):
        user.set_password(new_password)
        user.save()
        return Response({'success': 'Password changed successfully'})
    return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)


# user forgot password and wants to reset it by email
# TODO: send email with link to reset password
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password(request):
    email = request.data.get('email')
    user = User.objects.get(email=email)
    new_password = request.data.get('new_password')
    user.set_password(new_password)
    user.save()
    return Response({'success': 'Password changed successfully'})


'''
OTHER VIEWS
'''


@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_potential_partners(request):
    pass
    # user_profile = Profile.objects.get(user=request.user)
    # potential_partners = user_profile.get_potential_partners()
    # serializer = UserSerializer(potential_partners, many=True)
    # return Response(serializer.data)


@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_matches(request):
    pass
    # user_profile = Profile.objects.get(user=request.user)
    # matches = user_profile.get_matches()
    # serializer = UserSerializer(matches, many=True)
    # return Response(serializer.data)
