from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict\

from app.models import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

class NoteUpdate(BaseModel):
    title: str |None = Field(min_length=1, max_length=100)
    content: str | None = Field(min_length=1)

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    