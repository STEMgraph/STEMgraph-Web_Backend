# JSON-LD Primärdatenbank

import json, os
from fastapi.responses import JSONResponse
from config import STORAGE_DIR, LD_DATABASE, LD_CONTEXT_TEMPLATE
from services.storage import now, error_notFound


# auxiliary graph manipulation subroutines for JSON-LD graphs

def get_ld_graph():
    """Loads and returns the whole graph framework from the JSON-LD database."""
    with open(LD_DATABASE, 'r', encoding='utf-8') as f:
        wholeGraph = json.load(f)
    return wholeGraph

def init_ld_graph():
    """Returns an empty JSON-LD graph framework."""
    graph = {}
    add_ld_context(graph)
    add_ld_metadata(graph)
    graph["@graph"] = []
    return graph

def get_ld_exercise_node(uuid: str):
    """Get the list element with the given uuid from the JSON-LD database."""
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex["@id"] == uuid:
            return ex
    return error_notFound("uuid", uuid)

def get_ld_exercises_by_tag(field: str, search: str, subfield: str = None, match: str = "exact", lowercase: bool = True):
    """
    Returns a graph with all exercises where the given field contains the given value.
    - field: top-level field in each exercise (e.g. "keywords", "author")
    - value: the search term
    - subfield: optional subfield if field is a dict (e.g. "name")
    - match: "exact" or "partial"
    - lowercase: normalize values to lowercase if True
    """
    if lowercase:
        search = search.lower()
    exTagged = init_ld_graph()
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get(field) is not None:
            field_values = ex[field]
            if isinstance(field_values, str) or isinstance(field_values, dict):
                field_values = [field_values]
            for val in field_values:
                if isinstance(val, dict) and subfield:
                    val = val.get(subfield)
                if val is None:
                    continue
                if isinstance(val, str) and lowercase:
                    valCmp = val.lower()
                else:
                    valCmp = val
                if match == "exact" and search == valCmp:
                    exTagged["@graph"].append(ex)
                    break
                elif match == "partial" and isinstance(valCmp, str) and search in valCmp:
                    exTagged["@graph"].append(ex)
                    break
    return exTagged

def get_ld_path_to_exercise(uuid: str):
    """Returns a graph in JSON-LD format with all nodes leading to the given one."""
    path = init_ld_graph()
    path["@graph"].append(get_ld_exercise_node(uuid))
    if not isinstance(path, JSONResponse) and path.get("@graph"):
        visited = None
        expand_ld_dependencies(path, path["@graph"][0], visited)
    return path

def expand_ld_dependencies(data, curEx, visited):
    """Add the current exercise's dependencies to the JSON-LD graph."""
    if visited is None:
        visited = set()
    if curEx.get("dependsOn") is not None:
        for dep in curEx["dependsOn"]:
            if isinstance(dep, str):
                add_ld_exercise(data, dep, visited)
            elif isinstance(dep, dict) and dep.get("oneOf"):
                for alt in dep["oneOf"]:
                    add_ld_exercise(data, alt, visited)
            else:
                print("unexpected dependency structure in ", curEx["@id"], ": ", dep)

def add_ld_exercise(data, uuid, visited):
    """Adds an exercise to the JSON-LD data structure."""
    if uuid not in visited:
        visited.add(uuid)
        ex = get_ld_exercise_node(uuid)
        if not isinstance(ex, JSONResponse):
            data["@graph"].append(ex)
            expand_ld_dependencies(data, ex, visited)

def get_ld_end_nodes():
    """Returns all nodes that are not referenced by others (end points / final lessons)."""
    referenced_ids = set()
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get("dependsOn"):
            for dep in ex["dependsOn"]:
                if isinstance(dep, str):
                    referenced_ids.add(dep)
                elif isinstance(dep, dict):
                    if dep.get("@id"):
                        referenced_ids.add(dep["@id"])
                    if dep.get("oneOf"):
                        for alt in dep["oneOf"]:
                            referenced_ids.add(alt)
    ends = init_ld_graph()
    for ex in db["@graph"]:
        if ex["@id"] not in referenced_ids:
            ends["@graph"].append(ex)
    return ends

def get_ld_start_nodes():
    """Returns all nodes that have no dependencies (entry points / starting lessons)."""
    starts = init_ld_graph()
    db = get_ld_graph()
    for ex in db["@graph"]:
        deps = ex.get("dependsOn", [])
        if not deps or len(deps) == 0:
            starts["@graph"].append(ex)
    return starts

# routines to create the json-ld-database from the challenge-metadata files

def createdb_jsonld():
    """Creates challenges-ld.json from challenges' metadata."""
    db_jsonld = {}
    add_ld_context(db_jsonld)
    add_ld_metadata(db_jsonld)
    nodes = []
    for fname in os.listdir(STORAGE_DIR):
        if fname != 'metadata.json':
            file = os.path.join(STORAGE_DIR, fname)
            with open(file) as f:
                challenge_metadata= json.load(f)
            node = transform_challenge_metadata_to_ld(challenge_metadata) 
            nodes.append(node)
    db_jsonld["@graph"] = nodes
    with open(LD_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(db_jsonld, f, ensure_ascii=False, indent=2)

def add_ld_context(db_jsonld):
    """Gets context data from local context file."""
    with open(LD_CONTEXT_TEMPLATE) as context_file:
        context = json.load(context_file)
    db_jsonld["@context"] = context["@context"]

def add_ld_metadata(db_jsonld):
    """Creates metadata (url, created at & by)."""
    db_jsonld["@id"] = "https://stemgraph-api.boekelmann.net/"
    db_jsonld["generatedBy"] = {}
    db_jsonld["generatedBy"]["@type"] = "schema:Organization"
    db_jsonld["generatedBy"]["schema:name"] = "STEMgraph"
    db_jsonld["generatedBy"]["schema:url"] = "https://github.com/STEMgraph/"
    db_jsonld["generatedAt"] = now()

def transform_challenge_metadata_to_ld(md_json):
    """Transforms challenge metadata into a json-ld node."""
    node = {
        "@id": md_json["id"],
        "@type": "Exercise",
        "learningResourceType": "Exercise"
    }
    if "teaches" in md_json:
        node["teaches"] = md_json["teaches"]
    if "depends_on" in md_json:
        node["dependsOn"] = md_json["depends_on"]
    if "author" in md_json:
        author_list = md_json["author"]
        if isinstance(author_list, str):
            author_list = [author_list]
        node["author"] = []
        for author in author_list:
            node["author"].append({"@type": "Person", "name": author})
    if "first_used" in md_json:
        node["publishedAt"] = md_json["first_used"]
    if "keywords" in md_json:
        node["keywords"] = md_json["keywords"]
    return node
