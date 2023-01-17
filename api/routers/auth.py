from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database.db_setup import get_db
from ..database.models import User
from ..database import password
from ..schemas import token as token_schema
from ..oauth2 import create_token

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=token_schema.TokenResponse)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email does not exist"
        )
    
    if not password.match(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect password"
        )
    
    token = create_token(user.id)

    return token_schema.TokenResponse(access_token=token, token_type="bearer")
