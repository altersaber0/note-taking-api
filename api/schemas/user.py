from datetime import datetime

from pydantic import BaseModel, EmailStr, validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(value: str) -> str:
        if value.strip() == "":
            raise ValueError("Password cannot be empty")
        if not value.isalnum():
            raise ValueError("Password must be alpha-numeric")
        if len(value) < 8:
            raise ValueError("Password must be longer than 8 characters")
        return value


class UserInfo(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True