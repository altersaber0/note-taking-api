from fastapi import FastAPI

from .database.db_setup import engine, Base
from .routers import notes, groups, users, auth

# Create database and all tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# Initialize app and all routers
app = FastAPI(
    title="Note Taking API",
    description="""
    A small CRUD API for creating and managing text notes & groups of notes.
    You can sign up on POST /users to later get authenticated on POST /login.
    """
)

app.include_router(notes.router)
app.include_router(groups.router)
app.include_router(users.router)
app.include_router(auth.router)