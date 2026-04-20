from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from services.graph_ld import get_ld_graph, add_ld_metadata
from services.filters import get_count, get_list
from services.exporter import export_graph

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/")
def get_whole_graph(format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])):
    return export_graph(get_ld_graph(), format)

@router.get("/statistics")
def get_statistics():
    stats = {}
    add_ld_metadata(stats)
    stats["@type"] = "Statistics"
    stats["keywordCountDistinct"] = len(get_list("keywords"))
    stats["keywordCountTotal"] = sum(get_count("keywords").values())
    wholeGraph = get_ld_graph()
    stats["nodeCount"] = len(wholeGraph["@graph"])
    return stats
