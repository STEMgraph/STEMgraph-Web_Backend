from fastapi import APIRouter
from services.filters import get_count, get_list
from services.graph_ld import add_ld_metadata

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("/getKeywordCount")
def get_keyword_count():
    """Returns all keywords found along with their frequency."""
    keywordCount = {}
    add_ld_metadata(keywordCount)
    keywordCount["keywords"] = get_count("keywords")
    return keywordCount

@router.get("/getKeywordList")
def get_keyword_list():
    """Returns a list with all keywords found in the database."""
    keywordList = {}
    add_ld_metadata(keywordList)
    keywordList["keywords"] = get_list("keywords")
    return keywordList
