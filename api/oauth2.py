import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_HASHING_ALGORITHM = os.getenv("JWT_HASHING_ALGORITHM")

JWT_TOKEN_EXPIRATION_TIME_MINUTES = int(os.getenv("JWT_TOKEN_EXPIRATION_TIME_MINUTES"))

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


def create_token(user_id: int) -> str:
    
    # Add expiration field to the token
    expire = datetime.utcnow() + timedelta(minutes=JWT_TOKEN_EXPIRATION_TIME_MINUTES)
    
    payload = {"user_id": user_id, "exp": expire}

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_HASHING_ALGORITHM)

    return token


# Decrypt and get "user_id" field from token's payload
def decrypt_token(token: str, credentials_exception: HTTPException) -> int:
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_HASHING_ALGORITHM])

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    return user_id


# Dependency to be injected in endpoint functions
def get_current_user_id(token: str = Depends(oauth2_schema)) -> int:
    
    creadentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    user_id = decrypt_token(token, creadentials_exception)

    return user_id