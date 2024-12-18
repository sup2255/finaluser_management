from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re
from app.models.user_model import UserRole  # Ensure this import is correct
from app.utils.nickname_gen import generate_nickname  # Ensure this import works


# URL Validator
def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url


# Base User Schema
class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(
        default_factory=generate_nickname, min_length=3, pattern=r'^[\w-]+$', example="john_doe123"
    )
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: UserRole

    _validate_urls = validator(
        'profile_picture_url', 'linkedin_profile_url', 'github_profile_url',
        pre=True, allow_reuse=True
    )(validate_url)

    class Config:
        from_attributes = True


# User Creation Schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="Secure*1234")


# User Update Schema
class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=3, pattern=r'^[\w-]+$', example="john_doe123")
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Updated bio")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: Optional[str] = Field(None, example="AUTHENTICATED")

    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(values.get(field) for field in values if field != 'role'):
            raise ValueError("At least one field must be provided for update")
        return values


# User Response Schema
class UserResponse(UserBase):
    id: uuid.UUID = Field(..., example=str(uuid.uuid4()))
    is_professional: Optional[bool] = Field(default=False, example=True)


# Login Request Schema
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., min_length=6, example="Secure*1234")


# Error Response Schema
class ErrorResponse(BaseModel):
    error: str = Field(..., example="Not Found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")


# User List Response Schema
class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(
        ..., example=[{
            "id": str(uuid.uuid4()), "nickname": "john_doe123", "email": "john.doe@example.com",
            "first_name": "John", "last_name": "Doe", "bio": "Experienced developer",
            "role": "AUTHENTICATED",
            "profile_picture_url": "https://example.com/profiles/john.jpg",
            "linkedin_profile_url": "https://linkedin.com/in/johndoe",
            "github_profile_url": "https://github.com/johndoe",
            "is_professional": True
        }]
    )
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)
