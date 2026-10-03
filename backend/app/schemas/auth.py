
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong user password")

    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

class LoginSchema(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponseSchema(BaseModel):
    id: int
    email: str
    created_at: str | None = None

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponseSchema
