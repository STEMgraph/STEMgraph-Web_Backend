from fastapi import APIRouter
from services import filters

router = APIRouter(prefix="/keywords", tags=["keywords"])

@router.get("/")
def list_keywords():
    return {"message": "list of keywords"}

@router.get("/count")
def count_keywords():
    return {"message": "keyword count"}
