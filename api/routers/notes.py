from fastapi import APIRouter, HTTPException, status, Depends


router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)