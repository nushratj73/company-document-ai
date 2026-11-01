
from pydantic import BaseModel, EmailStr, Field


# Data required when an employee registers
class UserCreate(BaseModel):
    email: EmailStr

    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    password: str = Field(
        min_length=12,
        max_length=128
    )


# Data returned when a user is registered
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }
# Data required when an employee logs in
class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128
    )
 # Data returned after successful login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"   