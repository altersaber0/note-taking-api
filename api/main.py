from fastapi import FastAPI

from .database.db_setup import engine, Base
from .routers import notes, groups, users, auth


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notes.router)
app.include_router(groups.router)
app.include_router(users.router)
app.include_router(auth.router)