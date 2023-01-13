from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..database.db_setup import get_db
from ..database.models import Group, Note
from ..schemas import note as note_schema
from ..oauth2 import get_current_user_id


router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)


@router.post("/", response_model=note_schema.NoteInfo)
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