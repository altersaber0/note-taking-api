from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    content: str
    group_id: int


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    content: str


class NoteInfo(NoteCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Exclude user and group ids because Group already contains this information
class NoteInfoWithoutRelations(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True
      