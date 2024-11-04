from typing import List, NotRequired, TypedDict
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


class ProfileData(TypedDict, total=False):
    id: NotRequired[int]
    bio: NotRequired[str]
    interests: NotRequired[List[int]]
    picture_urls: NotRequired[List[str]]
    gender: NotRequired[str]
    location: NotRequired[str]
    preferred_gender: NotRequired[str]
    min_preferred_age: NotRequired[int]
    max_preferred_age: NotRequired[int]
    phone_number: NotRequired[str]
    height: NotRequired[int]
    pronouns: NotRequired[str]
    highest_education: NotRequired[str]
    political_views: NotRequired[str]
    pet_preferences: NotRequired[str]
    exercise_level: NotRequired[str]
    additional_info: NotRequired[str]
    occupation: NotRequired[str]
    goals: NotRequired[str]


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


# indexes of photos that will be updated
class PresignedUrlsRequest(TypedDict):
    photo_indexes: List[int]
