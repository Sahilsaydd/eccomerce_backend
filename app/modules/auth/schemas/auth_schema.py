from ast import pattern
from enum import Enum
from pydantic import BaseModel, EmailStr ,Field, field_validator

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    name:str
    email:EmailStr
    password:str = Field(min_length=8 ,max_length=20, description="Password must be 8-20 characters long, contain at least one letter and one number.")
    role:UserRole
    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")

        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number")

        return value

class LoginRequest(BaseModel):
    email:EmailStr
    password:str = Field(min_length=8 ,max_length=20, description="Password must be 8-20 characters long, contain at least one letter and one number.")
    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")

        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number")

        return value

class AuthResponse(BaseModel):
    access_token:str
    token_type:str
    