from fastapi import APIRouter
from services import filters

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/")
def list_authors():
    return {"message": "list of authors"}

@router.get("/count")
def count_authors():
    return {"message": "author count"}
