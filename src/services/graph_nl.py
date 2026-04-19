import json, os
from fastapi.responses import JSONResponse
from config import STORAGE_DIR, NL_DATABASE
from services.storage import error_notFound

# auxiliary graph manipulation subroutines for graphs in nodes-links JSON format

def get_nl_graph():
    """Loads and returns the whole graph framework from the nodes-links JSON database."""
    with open(NL_DATABASE, 'r', encoding='utf-8') as f:
        wholeGraph = json.load(f)
    return wholeGraph

def init_nl_graph():
    """Returns an empty nodes-links graph framework."""
    graph = {"nodes": [], "links": []}
    return graph

def get_nl_exercise_node(uuid: str):
    """Get the list element with the given uuid from the nodes-links JSON database."""
    db = get_nl_graph()
    for ex in db["nodes"]:
        if ex["id"] == uuid:
            return ex
    return error_notFound("uuid", uuid)

def add_nl_links(graph: dict):
    """Add links for the nodes in the given nodes-links graph."""
    db = get_nl_graph()
    node_ids = {node["id"] for node in graph["nodes"]}
    for link in db["links"]:
        if link["source"] in node_ids or link["target"] in node_ids:
            graph["links"].append(link)

def get_nl_path_to_exercise(uuid: str):
    """Returns a graph in nodes-links format with all nodes leading to the given one."""
    path = init_nl_graph()
    node = get_nl_exercise_node(uuid)
    if not isinstance(node, JSONResponse):
        path["nodes"].append(node)
        visited = None
        expand_nl_dependencies(path, node, visited)
    return path

def expand_nl_dependencies(data, curEx, visited):
    """Add the current exercise's dependencies to the nodes-links graph."""
    if visited is None:
        visited = set()
    db = get_nl_graph()
    for link in db["links"]:
        if link["target"] == curEx["id"]:
            source_id = link["source"]
            if source_id not in visited:
                visited.add(source_id)
                source_node = get_nl_exercise_node(source_id)
                if not isinstance(source_node, JSONResponse):
                    data["nodes"].append(source_node)
                    data["links"].append(link)
                    expand_nl_dependencies(data, source_node, visited)

def get_nl_exercises_by_tag(field: str, search: str, subfield: str = None, match: str = "exact", lowercase: bool = True):
    """
    Returns a nodes-links-graph with all exercises where the given field contains the given value.
    - field: top-level field in each exercise (e.g. "keywords", "author")
    - value: the search term
    - subfield: optional subfield if field is a dict (e.g. "name")
    - match: "exact" or "partial"
    - lowercase: normalize values to lowercase if True
    """
    if lowercase:
        search = search.lower()
    exTagged = init_nl_graph()
    db = get_nl_graph()
    for ex in db["nodes"]:
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
                    exTagged["nodes"].append(ex)
                    break
                elif match == "partial" and isinstance(valCmp, str) and search in valCmp:
                    exTagged["nodes"].append(ex)
                    break
    add_nl_links(exTagged)
    return exTagged

def get_nl_end_nodes():
    """Returns all nodes that are not referenced by others (end points / final lessons)."""
    referenced_ids = set()
    db = get_nl_graph()
    for link in db["links"]:
        referenced_ids.add(link["source"])
    ends = init_nl_graph()
    for ex in db["nodes"]:
        if ex["id"] not in referenced_ids:
            ends["nodes"].append(ex)
    add_nl_links(ends)
    return ends

def get_nl_start_nodes():
    """Returns all nodes that have no dependencies (entry points / starting lessons)."""
    dependent_ids = set()
    db = get_nl_graph()
    for link in db["links"]:
        dependent_ids.add(link["target"])
    starts = init_nl_graph()
    for ex in db["nodes"]:
        if ex["id"] not in dependent_ids:
            starts["nodes"].append(ex)
    add_nl_links(starts)
    return starts


# routines to create the node-link-database from the challenge-metadata files
# (for use with e.g. https://github.com/vasturiano/3d-force-graph)

def createdb_jsonnl():
    """Creates a node-link-structured .json from challenges' metadata."""
    db_jsonnl = {"nodes": [], "links": []}
    for fname in os.listdir(STORAGE_DIR):
        if fname != 'metadata.json':
            file = os.path.join(STORAGE_DIR, fname)
            with open(file) as f:
                challenge_metadata = json.load(f)
            node = get_node_from_challenge_metadata(challenge_metadata)
            db_jsonnl["nodes"].append(node)
            links = get_links_from_challenge_metadata(challenge_metadata)
            db_jsonnl["links"].extend(links)
    with open(NL_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(db_jsonnl, f, ensure_ascii=False, indent=2)

def get_node_from_challenge_metadata(md_json):
    """Transforms challenge metadata into a json node for node-link structure."""
    node = {
        "id": md_json["id"],
        "type": "Exercise"
    }
    if "teaches" in md_json:
        node["teaches"] = md_json["teaches"]
    if "author" in md_json:
        author_list = md_json["author"]
        if isinstance(author_list, str):
            author_list = [author_list]
        node["author"] = author_list
    if "first_used" in md_json:
        node["publishedAt"] = md_json["first_used"]
    if "keywords" in md_json:
        node["keywords"] = md_json["keywords"]
    return node

def get_links_from_challenge_metadata(md_json):
    """Transforms challenge metadata into json links for node-link structure."""
    links = []
    if "depends_on" in md_json:
        for dep in md_json["depends_on"]:
            if isinstance(dep, list):
                pass  # should not be expected, but ignore for now
            else:
                link = {
                    "source": dep,
                    "target": md_json["id"]
                }
            links.append(link)
    return links
