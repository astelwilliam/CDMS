from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class CurrentUser(BaseModel):
    """Schema for current authenticated user response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    role: str
    is_active: bool


class PersistentSession(BaseModel):
    user: CurrentUser
    csrf_token: str


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(
        ...,
        min_length=6,
        description="Current password"
    )

    new_password: str = Field(
        ...,
        min_length=6,
        description="New password"
    )
