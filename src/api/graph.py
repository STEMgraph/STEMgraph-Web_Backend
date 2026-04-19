from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.graph_ld import get_ld_graph, add_ld_metadata
from services.graph_nl import get_nl_graph
from services.filters import get_count, get_list


router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/getStatistics")
def get_statistics():
    """Returns several statistics about the graph."""
    stats = {}
    add_ld_metadata(stats)
    stats["@type"] = "Statistics"
    stats["keywordCountDistinct"] = len(get_list("keywords"))
    stats["keywordCountTotal"] = sum(get_count("keywords").values())
    wholeGraph = get_ld_graph()
    stats["nodeCount"] = len(wholeGraph["@graph"])
    return stats

@router.get("/getWholeGraph")
def get_whole_graph(format: str = Query("json", enum=["json", "json-ld"])):
    """Returns the whole graph, i.e. database."""
    if format == "json":
        wholeGraph = get_nl_graph()
        return JSONResponse(content=wholeGraph, media_type="application/json")
    elif format == "json-ld":
        wholeGraph = get_ld_graph()
        return JSONResponse(content=wholeGraph, media_type="application/ld+json") 
