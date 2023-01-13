from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    content: str
    group_id: int


class NoteInfo(NoteCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True