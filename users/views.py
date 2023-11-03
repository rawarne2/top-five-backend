from tokenize import TokenError
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer


@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_potential_partners(request):
    all_users = User.objects.all()
    serializer = UserSerializer(all_users, data=request.data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def get_user(request, user_id):
    user = User.objects.get(id=user_id)

    if user is not None and user.is_authenticated:
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response({'get_user error': 'Invalid user id or authentication'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@csrf_exempt
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.update(
            user,
            serializer.validated_data
        )
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@api_view(['DELETE'])
@csrf_exempt
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return Response({'success': 'User deleted successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    password = request.data.get('password')
    email = request.data.get('email')

    user_object = authenticate(request, email=email, password=password)

    if user_object:
        try:
            login(request, user_object)
            serializer = UserSerializer(user_object)
            user_data = serializer.data

            # TODO: handle DatabaseError for when outstanding token already exists
            refresh_token = RefreshToken.for_user(user_object)
            access_token = refresh_token.access_token

            tokens = {
                'access': str(access_token),
                'refresh': str(refresh_token)
            }
            user_object.save()
            return Response({'user': user_data, 'tokens': tokens})

        except Exception as err:
            return Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)
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

            return Response({'success': 'signed out!'}, status=200)
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token provided'}, status=400)
        except Exception as err:
            print('error logging out>>>', err)
            return Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'error': 'No refresh token provided.'}, status=400)


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def signup_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    else:
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
