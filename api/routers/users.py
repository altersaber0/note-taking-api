from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas import user as user_schema
from ..database.db_setup import get_db
from ..database.models import User
from ..database import password


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=user_schema.UserInfo)
def sign_up(new_user: user_schema.UserCreate, db: Session = Depends(get_db)):

    try:
        new_user.password = password.hash(new_user.password)
        user = User(**new_user.dict())
        db.add(user)
        db.commit()
        
    # except when UNIQUE constraint on users.email fails
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email already exists"
        )
    
    db.refresh(user)
    return user
