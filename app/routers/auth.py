from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.jwt import create_access_token
from app.dependencies import get_db, get_current_user
from app.core.security import verify_password, hash_password
from app.models import User, UserRole
from app.schemas import UserCreate, UserRead, Token

router = APIRouter(
    prefix="api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)

async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    # Check if the username or email already exists
    existing_user = await db.scalar(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # Hash the password before storing it
    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole.USER  # Default role for new users
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user due to database integrity error"
        )

    return new_user



