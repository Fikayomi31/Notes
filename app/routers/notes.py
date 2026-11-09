from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from  app.database import get_db
from app.schemas import NoteCreate, NoteResponse, NoteUpdate
from app.models import Note, User
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api/notes",
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

@router.get("/", response_model=list[NoteResponse])
async def get_notes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await db.scalars(
            select(Note)
            .where(Note.user_id == current_user.id)
            .order_by(Note.created_at.desc())
        )

        return result.all()
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the notes.",
)
    
@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        note = await db.scalar(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found."
            )
        return note
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the note.", 
        )


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    updates = {
        field: value
        for field, value in note_data.model_dump(exclude_unset=True).items()
        if value is not None
    }

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Provide at least one field to update (title or content).",
        )

    try:
        note = await db.scalar(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == current_user.id,
            )
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found.",
            )

        if "title" in updates:
            duplicate = await db.scalar(
                select(Note.id).where(
                    Note.title.ilike(updates["title"].strip()),
                    Note.user_id == current_user.id,
                    Note.id != note_id,
                )
            )
            if duplicate is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A note with the same title already exists for this user.",
                )

        for field, value in updates.items():
            setattr(note, field, value)

        await db.commit()
        await db.refresh(note)

        return note

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the note.",
        )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        note = await db.scalar(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found."
            )

        await db.delete(note)
        await db.commit()

        return {"detail": "Note deleted successfully."}

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the note.",
        )