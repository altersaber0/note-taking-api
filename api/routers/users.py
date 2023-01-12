from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..schemas import user as user_schema
from ..database.db_setup import get_db


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=user_schema.UserInfo)
def sign_up(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    ...