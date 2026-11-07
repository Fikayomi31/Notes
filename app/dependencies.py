from typing import Annotated
from collections.abc import AsyncGenerator


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.jwt import decode_access_token
from app.models import User

# Extract bearer token from request headers
bearer_scheme = HTTPBearer(auto_error=False)

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: DBSession = None,
) -> User:

    # Validate JWT token and retrieve the current user
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        user_id =  int(payload["sub"])

        if user_id <= 0:
            raise ValueError("Invalid user ID in token payload")

    except (ValueError, KeyError):
        raise unauthorized

    # retrieve the user from the database
    user = await db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise unauthorized

    return user
    
