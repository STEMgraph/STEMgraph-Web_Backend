from fastapi import BackgroundTasks, FastAPI, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from datetime import datetime
import base64, json, os, re, requests, time


# initialize global variables
ORG = os.environ['GITHUB_ORG']
GITHUB_PAT = os.environ['GITHUB_PAT']
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/graph-db/repos')
METADATA_FILE = os.path.join(STORAGE_DIR, 'metadata.json')
TEMPLATE_DIR = os.environ.get('TEMPLATE_DIR', '/graph-db/templates')
LD_CONTEXT_TEMPLATE = os.path.join(TEMPLATE_DIR, 'ld-context.json')
LD_METADATA_TEMPLATE = os.path.join(TEMPLATE_DIR, 'ld-metadata.json')
DATABASE_DIR = os.environ.get('DATABASE_DIR', '/graph-db')
LD_DATABASE = os.path.join(DATABASE_DIR, 'ld-database.json')
NL_DATABASE = os.path.join(DATABASE_DIR, 'nl-database.json')


# setup the api object
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["https://stemgraph.boekelmann.net"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def read_root():
    """Returns a greeting."""
    return {"message": "Welcome to STEMgraph API"}

@app.get("/getAuthorCount")
def get_author_count():
    """Returns all authors found along with their frequency."""
    authorCount = {}
    add_ld_metadata(authorCount)
    authorCount["authors"] = get_count("author", subfield="name", lowercase=False)
    return authorCount

@app.get("/getAuthorList")
def get_author_list():
    """Returns a list with the names of all authors found in the database."""
    authorList = {}
    add_ld_metadata(authorList)
    authorList["authors"] = get_list("author", subfield="name", lowercase=False)
    return authorList

@app.get("/getEndNodes")
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

@app.get("/getExercise/{uuid}")
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

@app.get("/getExercisesByAuthor/{name}")
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

@app.get("/getExercisesByKeyword/{keyword}")
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

@app.get("/getExercisesByTopic/{topic}")
def get_exercises_by_topic(topic: str, format: str = Query("json", enum=["json", "json-ld"])):
    """ Returns a graph with all exercises which include "topic" in the 'teaches' field."""
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

@app.get("/getKeywordCount")
def get_keyword_count():
    """Returns all keywords found along with their frequency."""
    keywordCount = {}
    add_ld_metadata(keywordCount)
    keywordCount["keywords"] = get_count("keywords")
    return keywordCount

@app.get("/getKeywordList")
def get_keyword_list():
    """Returns a list with all keywords found in the database."""
    keywordList = {}
    add_ld_metadata(keywordList)
    keywordList["keywords"] = get_list("keywords")
    return keywordList

@app.get("/getPathToExercise/{uuid}")
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

@app.get("/getStartNodes")
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

@app.get("/getStatistics")
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

@app.get("/getWholeGraph")
def get_whole_graph(format: str = Query("json", enum=["json", "json-ld"])):
    """Returns the whole graph, i.e. database."""
    if format == "json":
        wholeGraph = get_nl_graph()
        return JSONResponse(content=wholeGraph, media_type="application/json")
    elif format == "json-ld":
        wholeGraph = get_ld_graph()
        return JSONResponse(content=wholeGraph, media_type="application/ld+json") 

@app.post("/refreshDatabase")
async def refresh_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_challenge_db_task)
    return {"status": "refresh challenge database started"}


# auxiliary functions to get lists and counts of tags

def get_count(field: str, subfield: str = None, lowercase: bool = True):
    """
    Returns frequency counts for a given field in the database.
    - field: top-level field in each exercise
    - subfield: optional subfield if field is a dict
    - lowercase: normalize values to lowercase if True
    """
    counts = defaultdict(int)
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get(field) is not None:
            field_values = ex[field]
            if isinstance(field_values, str) or isinstance(field_values, dict):
                field_values = [field_values]
            for value in field_values:
                if isinstance(value, dict) and subfield:
                    value = value.get(subfield)
                if value is None:
                    continue
                if lowercase and isinstance(value, str):
                    value = value.lower()
                counts[value] += 1
    return dict(counts)

def get_list(field: str, subfield: str = None, lowercase: bool = True):
    """
    Returns a list of unique values for a given field in the database.
    - field: top-level field in each exercise (e.g. "keywords", "author")
    - subfield: optional subfield if field is a dict (e.g. "name")
    - lowercase: normalize values to lowercase if True
    """
    values = set()
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex.get(field) is not None:
            field_values = ex[field]
            if isinstance(field_values, str) or isinstance(field_values, dict):
                field_values = [field_values]
            for value in field_values:
                if isinstance(value, dict) and subfield:
                    value = value.get(subfield)
                if value is None:
                    continue
                if lowercase and isinstance(value, str):
                    value = value.lower()
                values.add(value)
    return sorted(list(values))


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

def add_nl_links(graph: str):
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

def get_ld_exercise_node(uuid: str):
    """Get the list element with the given uuid from the JSON-LD database."""
    db = get_ld_graph()
    for ex in db["@graph"]:
        if ex["@id"] == uuid:
            return ex
    return error_notFound("uuid", uuid)

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


# auxiliary functions to build / update the database cache

def get_pat():
    return GITHUB_PAT

def list_org_repos(token):
    url = f'https://api.github.com/orgs/{ORG}/repos?per_page=100'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    repos = []
    while url:
        r = requests.get(url, headers=headers); r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get('next', {}).get('url')
    return repos

def latest_commit_sha(token, owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{branch}'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers); r.raise_for_status()
    return r.json()['sha']

def fetch_readme_text(token, owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/readme'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return base64.b64decode(data['content']).decode('utf-8')

def extract_json_from_readme(readme_text):
    start = readme_text.find("<!---")
    end = readme_text.find("--->", start)
    if start == -1 or end == -1:
        return None
    block = readme_text[start+5:end].strip()
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        return None

def ensure_metadata():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE) as f:
            return json.load(f)
    return {}

def save_metadata(m):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)

def refresh_challenge_db_task():
    token = get_pat()
    repos = list_org_repos(token)
    meta = ensure_metadata()
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    has_db_changed = False
    for r in repos:
        name = r['name']
        owner, branch = r['owner']['login'], r['default_branch']
        sha = latest_commit_sha(token, owner, name, branch)
        print(f"Checking repo {name}, sha={sha}")
        if not uuid_pattern.match(name.lower()):
            print("Skipped: not UUID")
            continue
        if meta.get(name, {}).get('sha') != sha:
            readme_text = fetch_readme_text(token, owner, name)
            if readme_text:
                json_obj = extract_json_from_readme(readme_text)
                if json_obj:
                    filename = os.path.join(STORAGE_DIR, f'{name}__{sha}.json')
                    tmp = filename + '.tmp'
                    with open(tmp, 'w', encoding='utf-8') as f:
                        json.dump(json_obj, f, ensure_ascii=False, indent=2)
                    os.replace(tmp, filename)
                    meta[name] = {
                        'sha': sha,
                        'downloaded_at': int(time.time()),
                        'path': filename
                    }
                    has_db_changed = True
            if not readme_text:
                print("Skipped: no README")
            elif not json_obj:
                print("Skipped: no valid JSON block")
            else:
                print("Saved JSON for", name)
    if has_db_changed:
        save_metadata(meta)
        print("All metadata from STEMgraph challenges fetched.")
        createdb_jsonld()
        print("Database created as JSON-LD.")
        createdb_jsonnl()
        print("Database created as node-link JSON.")


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


# routines to create the node-link-database from the challenge-metadata files
# (for use with e.g. https://github.com/vasturiano/3d-force-graph)

def createdb_jsonnl():
    """Creates a node-link-structured .json from challenges' metadata."""
    db_jsonnl = {"nodes": [], "links": []}
    for fname in os.listdir(STORAGE_DIR):
        if fname != 'metadata.json':
            file = os.path.join(STORAGE_DIR, fname)
            with open(file) as f:
                challenge_metadata= json.load(f)
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


# lightweight and error functions

def now():
    """Gets the current timestamp."""
    return datetime.utcnow().isoformat() + "Z"

def error_notFound(field, value):
    """Returns a customized error message for searches with no result."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"No exercises found for {field}: '{value}'"}
    )
