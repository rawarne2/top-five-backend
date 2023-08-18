from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer


@api_view(['GET'])
@csrf_exempt
def get_all_users(request):
    all_users = User.objects.all()
    serializer = UserSerializer(all_users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@csrf_exempt
def get_user(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['PUT'])
@csrf_exempt
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
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
@csrf_exempt
def login_view(request):
    password = request.data.get('password')
    username = request.data.get('username')
    print(request, username, password)
    user = authenticate(request, username=username, password=password)
    print(user)
    if user is not None:
        print(user)
        login(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def logout_view(request):
    logout(request)
    return Response({'success': 'Logged out successfully'})


@api_view(['POST'])
@csrf_exempt
def signup_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
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
@csrf_exempt
def reset_password(request):
    email = request.data.get('email')
    user = User.objects.get(email=email)
    new_password = request.data.get('new_password')
    user.set_password(new_password)
    user.save()
    return Response({'success': 'Password changed successfully'})
