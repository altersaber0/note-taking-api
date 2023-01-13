from datetime import datetime

from pydantic import BaseModel, Field

from .note import NoteInfoWithoutRelations


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class GroupInfo(GroupCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GroupWithNotes(BaseModel):
    group: GroupInfo
    notes: list[NoteInfoWithoutRelations]

    class Config:
        orm_mode = True
