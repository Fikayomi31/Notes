from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, exc
from collections.abc import AsyncGenerator

from app.core.jwt import decode_access_token
from app.database import AsyncSessionLocal
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api//auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: AsyncSession = Depends(get_db)
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id =  int(payload["sub"])

        if user_id <= 0:
            raise ValueError("Invalid user ID in token payload")

    except (ValueError, InvalidTokenError):
        raise unauthorized from exc

    user = await db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise unauthorized

    return user
    
