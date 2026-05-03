from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.exporter import export_graph
import services.graph_ld
import services.storage


router = APIRouter(prefix="/exercises", tags=["exercises"])


# ---------------------------------------------------------
# LIST EXERCISES (with filters)
# ---------------------------------------------------------
@router.get("/")
def list_exercises(
    author: str = None,
    keyword: str = None,
    topic: str = None,
    match: str = Query("exact", enum=["exact", "partial"]),
    format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])
):
    """
    List exercises with optional filters.
    JSON-LD is always the primary source.
    """

    # 1. Primärdatenbank laden
    ld_data = services.graph_ld.get_ld_graph()
    filtered = {"@graph": []}

    # 2. Filterfunktion
    def matches(ex):
        # AUTHOR
        if author:
            authors = ex.get("author", [])
            names = [a.get("name", "").lower() for a in authors]
            if match == "exact" and author.lower() not in names:
                return False
            if match == "partial" and not any(author.lower() in n for n in names):
                return False

        # KEYWORD
        if keyword:
            kws = [k.lower() for k in ex.get("keywords", [])]
            if match == "exact" and keyword.lower() not in kws:
                return False
            if match == "partial" and not any(keyword.lower() in k for k in kws):
                return False

        # TOPIC (teaches)
        if topic:
            teaches = ex.get("teaches", "")
            teaches_list = teaches if isinstance(teaches, list) else [teaches]
            teaches_list = [t.lower() for t in teaches_list]
            if not any(topic.lower() in t for t in teaches_list):
                return False

        return True

    # 3. Filter anwenden
    for ex in ld_data["@graph"]:
        if matches(ex):
            filtered["@graph"].append(ex)

    # 4. Ausgabe
    return export_graph(filtered, format)


# ---------------------------------------------------------
# START NODES
# ---------------------------------------------------------
@router.get("/start-nodes")
def get_start_nodes(format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])):
    """Return exercises with no dependencies."""

    data = services.graph_ld.get_ld_start_nodes()
    if isinstance(data, JSONResponse):
        return data
    return export_graph(data, format)


# ---------------------------------------------------------
# END NODES
# ---------------------------------------------------------
@router.get("/end-nodes")
def get_end_nodes(format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])):
    """Return exercises with no outgoing edges."""

    data = services.graph_ld.get_ld_end_nodes()
    if isinstance(data, JSONResponse):
        return data
    return export_graph(data, format)


# ---------------------------------------------------------
# SINGLE EXERCISE
# ---------------------------------------------------------
@router.get("/{uuid}")
def get_exercise(uuid: str, format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])):
    """Returns a graph with one single exercise node."""
    node = services.graph_ld.get_ld_exercise_node(uuid)
    if isinstance(node, JSONResponse):
        return node

    ld = services.graph_ld.init_ld_graph()
    ld["@graph"].append(node)

    return export_graph(ld, format)


# ---------------------------------------------------------
# PATH TO EXERCISE
# ---------------------------------------------------------
@router.get("/{uuid}/path")
def get_path_to_exercise(uuid: str, format: str = Query("jsonld", enum=["jsonld", "nodelink", "yaml"])):
    """Return dependency path to exercise."""
    data = services.graph_ld.get_ld_path_to_exercise(uuid)
    if isinstance(data, JSONResponse):
        return data
    return export_graph(data, format)
    