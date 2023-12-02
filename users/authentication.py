from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class NoRefreshJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Call the parent class to perform default JWT authentication
        user, validated_token = super().authenticate(request)

        # Check if the token used for authentication is a refresh token
        if validated_token and validated_token['token_type'] == 'refresh':
            raise AuthenticationFailed(
                "Refresh tokens are not allowed for authentication.")

        return user, validated_token
