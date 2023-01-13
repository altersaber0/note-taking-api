from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..database.db_setup import get_db
from ..database.models import Group, Note
from ..schemas import group as group_schema
from ..oauth2 import get_current_user_id


router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


@router.post("/", response_model=group_schema.GroupInfo, status_code=status.HTTP_201_CREATED)
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