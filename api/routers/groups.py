from fastapi import APIRouter, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..database.db_setup import get_db
from ..database.models import Group, Note
from ..schemas import group as group_schema
from ..oauth2 import get_current_user_id

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post(
    "/",
    response_model=group_schema.GroupInfo,
    status_code=status.HTTP_201_CREATED
)
def create_group(
    group: group_schema.GroupCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):

    new_group = group.dict()
    new_group.update({"user_id": current_user_id})

    new_group = Group(**new_group)

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


@router.get("/", response_model=list[group_schema.GroupWithNotes])
def get_all_groups_with_notes(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    
    results = db\
        .query(Group, Note)\
        .filter(Group.user_id == current_user_id)\
        .join(Note, Group.id == Note.group_id, isouter=True)\
        .group_by(Note.id)\
        .all()

    # Filter rows to get all unique groups
    groups = list({result[0] for result in results})

    # Add all notes to corresponding groups' ["notes"] key
    groups_with_notes = []
    
    for group in groups:
        group_with_notes = {"group": group, "notes": []}

        for note in (result[1] for result in results):
            if note:
                if note.group_id == group.id:
                    group_with_notes["notes"].append(note)
            else:
                continue

        groups_with_notes.append(group_with_notes)

    return groups_with_notes


@router.get("/{id}", response_model=group_schema.GroupWithNotes)
def get_group_with_notes_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    
    group = db.query(Group).filter(Group.id == id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested group id does not exist"
        )
    
    if group.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to see other users' groups"
        )
    
    results = db\
        .query(Group, Note)\
        .join(Note, Group.id == Note.group_id)\
        .group_by(Note.id)\
        .filter(Group.id == id)\
        .all()

    return group_schema.GroupWithNotes(
        group=group,
        notes=[result[1] for result in results]
    )


@router.put("/{id}", response_model=group_schema.GroupInfo)
def update_group_by_id(
    id: int,
    updated_group: group_schema.GroupCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):

    query = db.query(Group).filter(Group.id == id)

    group = query.first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested group id does not exist"
        )
    
    if group.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update other users' groups"
        )

    query.update(updated_group.dict())
    db.commit()
    db.refresh(group)
    
    return group


@router.delete("/{id}")
def delete_group_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):
    
    query = db.query(Group).filter(Group.id == id)

    group = query.first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested group id does not exist"
        )
    
    if group.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete other users' groups"
        )
    
    query.delete(synchronize_session=False)

    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
