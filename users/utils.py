from users.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


def get_user_from_db(user_id: int) -> User | Response:
    try:
        return User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
