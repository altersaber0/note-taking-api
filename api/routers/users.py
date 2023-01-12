from fastapi import APIRouter, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database.db_setup import get_db
from ..database.models import User
from ..database import password
from ..schemas import user as user_schema
from ..oauth2 import get_current_user_id


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=user_schema.UserInfo
)
def sign_up(new_user: user_schema.UserCreate, db: Session = Depends(get_db)):

    try:
        new_user.password = password.hash(new_user.password)
        user = User(**new_user.dict())
        db.add(user)
        db.commit()
        
    # when UNIQUE constraint on users.email fails (email already exists)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email already exists"
        )
    
    db.refresh(user)

    return user


@router.put("/{id}", response_model=user_schema.UserInfo)
def update_user(
    id: int,
    updated_data: user_schema.UserCreate,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):

    query = db.query(User).filter(User.id == id)

    user = query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested user id does not exist"
        )
    
    if id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update other users' information"
        )
    
    query.update(updated_data.dict())

    db.commit()

    db.refresh(user)

    return user


@router.delete("/{id}", response_model=user_schema.UserInfo)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user_id = Depends(get_current_user_id)
):

    query = db.query(User).filter(User.id == id)

    user = query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested user id does not exist"
        )
    
    if id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete other users"
        )
    
    query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
