from fastapi import APIRouter, HTTPException, status, Depends


router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)