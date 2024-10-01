from typing import List, Tuple, TypedDict
from datetime import date


class UserCreateData(TypedDict):
    email: str
    password: str
    first_name: str
    last_name: str
    birthdate: date


class UserUpdateData(TypedDict, total=False):
    first_name: str
    last_name: str
    birthdate: date


class DeleteUserData(TypedDict):
    refresh_token: str


class ProfileUpdateData(TypedDict, total=False):
    bio: str
    interests: List[int]
    picture_urls: List[Tuple[int, str]]
    gender: str
    location: str
    preferred_gender: str
    min_preferred_age: int
    max_preferred_age: int
    phone_number: str


class ProfileData(ProfileUpdateData):
    user: int  # User ID


class MatchData(TypedDict):
    id: int
    first_name: str
    picture_url: str


class MatchesResponse(TypedDict):
    matches: List[MatchData]


class PotentialMatchesResponse(TypedDict):
    potential_matches: List[MatchData]


class LoginData(TypedDict):
    email: str
    password: str


class PasswordChangeData(TypedDict):
    old_password: str
    new_password: str


class PasswordResetData(TypedDict):
    new_password: str


class LogoutData(TypedDict):
    refresh_token: str


class PresignedUrlsRequest(TypedDict):
    photo_count: List[int]


class PresignedUrl(TypedDict):
    index: int
    url: str


class PresignedUrlsResponse(TypedDict):
    presigned_urls: List[PresignedUrl]
