import os
import secrets

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

if len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes
