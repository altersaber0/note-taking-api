from fastapi import APIRouter, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..database.db_setup import get_db
from ..database.models import Group, Note
from ..schemas import note as note_schema
from ..oauth2 import get_current_user_id


router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)


@router.post("/", response_model=note_schema.NoteInfo, status_code=status.HTTP_201_CREATED)
def create_note(
    note: note_schema.NoteCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):

    group = db.query(Group).filter(Group.id == note.group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Group id {note.group_id} does not exist"
        )
    
    if group.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not allowed to create notes in other users' groups"
        )

    new_note = note.dict()
    new_note.update({"user_id": current_user_id})

    new_note = Note(**new_note)

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.get("/", response_model=list[note_schema.NoteInfo])
def get_all_notes(
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):

    notes = db.query(Note).filter(Note.user_id == current_user_id).all()
    
    return notes


@router.get("/{id}", response_model=note_schema.NoteInfo)
def get_note_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):
    
    note = db.query(Note).filter(Note.id == id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested note id does not exist"
        )
    
    if note.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to see other users' notes"
        )
    
    return note


@router.put("/{id}", response_model=note_schema.NoteInfo)
def update_note_by_id(
    id: int,
    updated_note: note_schema.NoteUpdate,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):

    query = db.query(Note).filter(Note.id == id)

    note = query.first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested note id does not exist"
        )
    
    if note.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update other users' notes"
        )

    query.update(updated_note.dict())
    db.commit()
    db.refresh(note)
    
    return note


@router.delete("/{id}")
def delete_note_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):
    
    query = db.query(Note).filter(Note.id == id)

    note = query.first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested note id does not exist"
        )
    
    if note.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete other users' notes"
        )
    
    query.delete(synchronize_session=False)

    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
