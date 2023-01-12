from fastapi import FastAPI

from .database.db_setup import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI()