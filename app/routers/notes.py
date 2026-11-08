from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

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

    try:
        # Check whether the same book already exists for the user
        statement = select(Note).where(
            Note.title.ilike(note_data.title.strip()),
            Note.user_id == current_user.id,
        )

        result = await db.execute(statement)

        existing_note = result.scalars().first()
        if existing_note:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A note with the same title already exists for this user.",
            )


        # If no existing note is found, create a new one
        new_note = Note(
            title=note_data.title,
            content=note_data.content,
            user_id=current_user.id,
        )

        db.add(new_note)

        await db.commit()
        await db.refresh(new_note)

        return new_note

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the note.",
        )

    
