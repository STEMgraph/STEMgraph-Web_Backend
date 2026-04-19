from fastapi import APIRouter
from services.filters import get_count, get_list
from services.graph_ld import add_ld_metadata

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("/")
def list_authors():
    """Returns a list with the names of all authors found in the database."""
    authorList = {}
    add_ld_metadata(authorList)
    authorList["authors"] = get_list("author", subfield="name", lowercase=False)
    return authorList

@router.get("/count")
def count_authors():
    """Returns all authors found along with their frequency."""
    authorCount = {}
    add_ld_metadata(authorCount)
    authorCount["authors"] = get_count("author", subfield="name", lowercase=False)
    return authorCount
