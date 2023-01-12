from fastapi import APIRouter, HTTPException, status, Depends


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)