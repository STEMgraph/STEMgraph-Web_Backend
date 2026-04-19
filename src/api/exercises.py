from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.graph_ld import (
    init_ld_graph, get_ld_exercise_node, get_ld_exercises_by_tag,
    get_ld_path_to_exercise, get_ld_start_nodes, get_ld_end_nodes
)
from services.graph_nl import (
    init_nl_graph, get_nl_exercise_node, get_nl_exercises_by_tag,
    get_nl_path_to_exercise, get_nl_start_nodes, get_nl_end_nodes, add_nl_links
)
from services.storage import error_notFound


router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.get("/")
def list_exercises(
    author: str = None,
    keyword: str = None,
    topic: str = None,
    format: str = Query("jsonld", enum=["jsonld", "nodelink", "xml"])
):
    return {"message": "list of exercises"}


@router.get("/{uuid}")
def get_exercise(uuid: str, format: str = Query("json", enum=["json", "json-ld"])):
    """Returns a graph with one single exercise node."""
    if format == "json":
        ex = init_nl_graph()
        node = get_nl_exercise_node(uuid)
        if isinstance(node, JSONResponse):
            return node
        ex["nodes"].append(node)
        add_nl_links(ex)
        return JSONResponse(content=ex, media_type="application/json")
    elif format == "json-ld":
        ex = init_ld_graph()
        node = get_ld_exercise_node(uuid)
        if isinstance(node, JSONResponse):
            return node
        ex["@graph"].append(node)
        return JSONResponse(content=ex, media_type="application/ld+json")

@router.get("/author")
def get_exercises_by_author(
    name: str,
    match: str = Query("exact", regex="^(exact|partial)$"),
    format: str = Query("json", enum=["json", "json-ld"])
):
    """
    Returns a graph with all exercises tagged with a specific author.
    The 'match' parameter controls whether the search is exact or partial.
    """
    if format == "json":
        exTagged = get_nl_exercises_by_tag("author", name, subfield="name", match=match)
        if not exTagged["nodes"]:
            return error_notFound("author", name)
        return JSONResponse(content=exTagged, media_type="application/json")
    elif format == "json-ld":
        exTagged = get_ld_exercises_by_tag("author", name, subfield="name", match=match)
        if not exTagged["@graph"]:
            return error_notFound("author", name)
        return JSONResponse(content=exTagged, media_type="application/ld+json")

@router.get("/keyword")
def get_exercises_by_keyword(
    keyword: str,
    match: str = Query("exact", regex="^(exact|partial)$"),
    format: str = Query("json", enum=["json", "json-ld"])
):
    """
    Returns a graph with all exercises tagged with a specific keyword.
    The 'match' parameter controls whether the search is exact or partial.
    """
    if format == "json":
        exTagged = get_nl_exercises_by_tag("keywords", keyword, match=match)
        if not exTagged["nodes"]:
            return error_notFound("keyword", keyword)
        return JSONResponse(content=exTagged, media_type="application/json")
    elif format == "json-ld":
        exTagged = get_ld_exercises_by_tag("keywords", keyword, match=match)
        if not exTagged["@graph"]:
            return error_notFound("keyword", keyword)
        return JSONResponse(content=exTagged, media_type="application/ld+json")

@router.get("/topic")
def get_exercises_by_topic(topic: str, format: str = Query("json", enum=["json", "json-ld"])):
    """Returns a graph with all exercises which include "topic" in the 'teaches' field."""
    if format == "json":
        exTopic = get_nl_exercises_by_tag("teaches", topic, match="partial")
        if not exTopic["nodes"]:
            return error_notFound("teaches", topic)
        return JSONResponse(content=exTopic, media_type="application/json")
    elif format == "json-ld":
        exTopic = get_ld_exercises_by_tag("teaches", topic, match="partial")
        if not exTopic["@graph"]:
            return error_notFound("teaches", topic)
        return JSONResponse(content=exTopic, media_type="application/ld+json")

@router.get("/{uuid}/path")
def get_path_to_exercise(uuid: str, format: str = Query("json", enum=["json", "json-ld"])):
    """Returns a graph with all nodes leading to the given one."""
    if format == "json":
        path = get_nl_path_to_exercise(uuid)
        if isinstance(path, JSONResponse):
            return path
        return JSONResponse(content=path, media_type="application/json")
    elif format == "json-ld":
        path = get_ld_path_to_exercise(uuid)
        if isinstance(path, JSONResponse):
            return path
        return JSONResponse(content=path, media_type="application/ld+json")

@router.get("/start-nodes")
def get_start_nodes(format: str = Query("json", enum=["json", "json-ld"])):
    """Returns all nodes that have no dependencies (entry points / starting lessons)."""
    if format == "json":
        starts = get_nl_start_nodes()
        if isinstance(starts, JSONResponse):
            return starts
        return JSONResponse(content=starts, media_type="application/json")
    elif format == "json-ld":
        starts = get_ld_start_nodes()
        if isinstance(starts, JSONResponse):
            return starts
        return JSONResponse(content=starts, media_type="application/ld+json")

@router.get("/end-nodes")
def get_end_nodes(format: str = Query("json", enum=["json", "json-ld"])):
    """Returns all nodes that are not referenced by others (end points / final lessons)."""
    if format == "json":
        end_nodes = get_nl_end_nodes()
        if isinstance(end_nodes, JSONResponse):
            return end_nodes
        return JSONResponse(content=end_nodes, media_type="application/json")
    elif format == "json-ld":
        end_nodes = get_ld_end_nodes()
        if isinstance(end_nodes, JSONResponse):
            return end_nodes
        return JSONResponse(content=end_nodes, media_type="application/ld+json")
    