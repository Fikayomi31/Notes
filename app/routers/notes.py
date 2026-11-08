from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from  app.database import get_db
from app.schemas import NoteCreate, NoteResponse, NoteUpdate
from app.models import Note
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api.notes",
    tags=["Notes"],
)

@router.post(
    "/",
    response_model=NoteResponse,
    status_code=201,
)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id,
    )

    db.add(new_note)

    await db.commit()
    await db.refresh(new_note)

    return new_note
