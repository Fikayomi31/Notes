from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import (
    ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

def create_acces_token(subject: str) -> str:
    expired_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": subject,
        "exp": expired_at
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise jwt.InvalidTokenError("Invalid subject in token payload")

        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
