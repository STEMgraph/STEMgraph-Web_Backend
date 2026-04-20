from fastapi import APIRouter
from services.filters import get_count, get_list
from services.graph_ld import add_ld_metadata

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/")
def list_authors():
    data = {}
    add_ld_metadata(data)
    data["authors"] = get_list("author", subfield="name", lowercase=False)
    return data

@router.get("/count")
def count_authors():
    data = {}
    add_ld_metadata(data)
    data["authors"] = get_count("author", subfield="name", lowercase=False)
    return data
