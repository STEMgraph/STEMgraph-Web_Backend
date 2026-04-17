from fastapi import APIRouter

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/statistics")
def get_statistics():
    return {"message": "graph statistics"}

@router.get("/whole")
def get_whole_graph(format: str = "jsonld"):
    return {"message": "whole graph"}
