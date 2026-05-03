from fastapi import APIRouter
from services.filters import get_count, get_list
from services.graph_ld import add_ld_metadata

router = APIRouter(prefix="/keywords", tags=["keywords"])

@router.get("/")
def list_keywords():
    data = {}
    add_ld_metadata(data)
    data["keywords"] = get_list("keywords")
    return data

@router.get("/count")
def count_keywords():
    data = {}
    add_ld_metadata(data)
    data["keywords"] = get_count("keywords")
    return data
