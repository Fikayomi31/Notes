from fastapi import FastAPI, Depends

from app.core.permissions import require_role
from app.models import UserRole
from app.routers.auth import router as auth_router
from app.routers.notes import router as notes_router

app = FastAPI(
    title="User Authentication API",
    description="A simple user authentication API built with FastAPI and SQLAlchemy.",
)

app.include_router(auth_router)
app.include_router(notes_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the User Authentication API!"}


@app.get("/api/user-area")
async def user_area(
    current_user=Depends(require_role(UserRole.USER)),
):
    return {
        "message": "Welcome to the user area.",
        "username": current_user.username,
        "role": current_user.role.value
    }

@app.get("/api/admin-area")
async def admin_area(
    current_user=Depends(require_role(UserRole.ADMIN))
):
    return {
        "message": "Welcome to the admin area",
        "username": current_user.username,
        "role": current_user.role.value
    }
