from fastapi import APIRouter, Query
from formats.jsonld_export import JsonLDExporter
from formats.nodelink_export import NodeLinkExporter
from formats.xml_export import XmlExporter

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
def get_exercise(uuid: str, format: str = "jsonld"):
    return {"message": f"exercise {uuid}"}

@router.get("/{uuid}/path")
def get_path(uuid: str, format: str = "jsonld"):
    return {"message": f"path to {uuid}"}

@router.get("/start-nodes")
def get_start_nodes(format: str = "jsonld"):
    return {"message": "start nodes"}

@router.get("/end-nodes")
def get_end_nodes(format: str = "jsonld"):
    return {"message": "end nodes"}
