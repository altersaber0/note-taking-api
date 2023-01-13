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


