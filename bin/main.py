from fastapi import BackgroundTasks, FastAPI, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from datetime import datetime
import base64, copy, json, os, re, requests, time


# initialize global variables

ORG = os.environ['GITHUB_ORG']
PAT_FILE = os.environ['GITHUB_PAT_FILE']
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/repos')
METADATA_FILE = os.path.join(STORAGE_DIR, 'metadata.json')
DATABASE_DIR = os.environ.get('DATABASE_DIR', '/data')
DATABASE_JSON = os.path.join(DATABASE_DIR, 'challenge_db.json')
CONTEXT_JSON = os.path.join(DATABASE_DIR, 'graphContext.json')

# --- to-do: check & put values into env-variables
# DB_LOC = "/data/jsonld.json"
# CONTEXT_LOC = "/app/data/graphContext.json"
# with open(DB_LOC) as db_file:
#    db = json.load(db_file)


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
    add_graph_metadata(authorCount)
    authorCount["authors"] = get_count("author", subfield="name", lowercase=False)
    return authorCount

@app.get("/getAuthorList")
def get_author_list():
    """Returns a list with the names of all authors found in the database."""
    authorList = {}
    add_graph_metadata(authorList)
    authorList["authors"] = get_list("author", subfield="name", lowercase=False)
    return authorList

@app.get("/getExercise/{uuid}")
def get_exercise(uuid: str):
    """Returns a graph with one single exercise node."""
    ex = get_exercise_node(uuid)
    if ex is None:
        return error_notFound("uuid", uuid)
    exercise = init_graph()
    exercise["@graph"].append(ex)
    return exercise

@app.get("/getExercisesByAuthor/{name}")
def get_exercises_by_author(
    name: str,
    match: str = Query("exact", regex="^(exact|partial)$")
):
    """
    Returns a graph with all exercises tagged with a specific author.
    The 'match' parameter controls whether the search is exact or partial.
    """
    exTagged = get_exercises_by_tag("author", name, subfield="name", match=match)
    if not exTagged["@graph"]:
        return error_notFound("author", name)
    return exTagged

@app.get("/getExercisesByKeyword/{keyword}")
def get_exercises_by_keyword(
    keyword: str,
    match: str = Query("exact", regex="^(exact|partial)$")
):
    """
    Returns a graph with all exercises tagged with a specific keyword.
    The 'match' parameter controls whether the search is exact or partial.
    """
    exTagged = get_exercises_by_tag("keywords", keyword, match=match)
    if not exTagged["@graph"]:
        return error_notFound("keyword", keyword)
    return exTagged

@app.get("/getExercisesByTopic/{topic}")
def get_exercises_by_topic(topic: str):
    """ Returns a graph with all exercises which include "topic" in the 'teaches' field."""
    exTopic = get_exercises_by_tag("teaches", topic, match="partial")
    if not exTopic["@graph"]:
        return error_notFound("teaches", topic)
    return exTopic

@app.get("/getKeywordCount")
def get_keyword_count():
    """Returns all keywords found along with their frequency."""
    keywordCount = {}
    add_graph_metadata(keywordCount)
    keywordCount["keywords"] = get_count("keywords")
    return keywordCount

@app.get("/getKeywordList")
def get_keyword_list():
    """Returns a list with all keywords found in the database."""
    keywordList = {}
    add_graph_metadata(keywordList)
    keywordList["keywords"] = get_list("keywords")
    return keywordList

@app.get("/getPathToExercise/{uuid}")
def get_path_to_exercise(uuid: str):
    """Returns a graph with all nodes leading to the given one."""
    path = get_exercise(uuid)
    if not isinstance(path, JSONResponse) and path.get("@graph"):
        visited = None
        expand_dependencies(path, path["@graph"][0], visited)
    return path

@app.get("/getStatistics")
def get_statistics():
    """Returns several statistics about the graph."""
    stats = {}
    add_graph_metadata(stats)
    stats["@type"] = "Statistics"
    stats["keywordCountDistinct"] = len(get_list("keywords"))
    stats["keywordCountTotal"] = sum(get_count("keywords").values())
    stats["nodeCount"] = len(db["@graph"])
    return stats

@app.get("/getWholeGraph")
def get_whole_graph():
    """Returns the whole graph, i.e. database."""
    wholeGraph = copy.deepcopy(db)
    wholeGraph["generatedAt"] = now()
    return wholeGraph 

@app.post("/refreshDatabase")
async def refresh_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_challenge_db_task)
    return {"status": "refresh challenge database started"}


# auxiliary graph manipulation subroutines

def init_graph():
    """Returns an empty graph framework."""
    graph = {}
    add_graph_context(graph)
    add_graph_metadata(graph)
    graph["@graph"] = []
    return graph

def get_count(field: str, subfield: str = None, lowercase: bool = True):
    """
    Returns frequency counts for a given field in the database.
    - field: top-level field in each exercise
    - subfield: optional subfield if field is a dict
    - lowercase: normalize values to lowercase if True
    """
    counts = defaultdict(int)
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

def get_exercises_by_tag(field: str, search: str, subfield: str = None, match: str = "exact", lowercase: bool = True):
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
    exTagged = init_graph()
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

def get_exercise_node(uuid: str):
    """Get the list element with the given uuid as @id."""
    for ex in db["@graph"]:
        if ex["@id"] == uuid:
            return ex
    return None

def expand_dependencies(data, curEx, visited):
    """Add the current exercise's dependencies to the graph."""
    if visited is None:
        visited = set()
    if curEx.get("dependsOn") is not None:
        for dep in curEx["dependsOn"]:
            if isinstance(dep, str):
                add_exercise(data, dep, visited)
            elif isinstance(dep, dict) and dep.get("oneOf"):
                for alt in dep["oneOf"]:
                    add_exercise(data, alt, visited)
            else:
                print("unexpected dependency structure in ", curEx["@id"], ": ", dep)

def add_exercise(data, uuid, visited):
    """Adds an exercise to the data structure."""
    if uuid not in visited:
        visited.add(uuid)
        ex = get_exercise_node(uuid)
        if ex is not None:
            data["@graph"].append(ex)
            expand_dependencies(data, ex, visited)

def add_graph_context(data):
    """Gets context data from local context file and adds it to the data."""
    with open(CONTEXT_LOC) as context_file:
        context = json.load(context_file)
    data["@context"] = context["@context"]

def add_graph_metadata(data):
    """Adds metadata (url, created at & by) to the data."""
    data["@id"] = "https://example.com/"
    data["generatedBy"] = {}
    data["generatedBy"]["@type"] = "schema:Organization"
    data["generatedBy"]["schema:name"] = "STEMgraph API"
    data["generatedBy"]["schema:url"] = "https://github.com/STEMgraph/API"
    data["generatedAt"] = now()


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


# auxiliary functions to build / update the database

def get_pat():
    with open(PAT_FILE, 'r') as f:
        return f.read().strip()

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
    with open(METADATA_FILE, 'w') as f:
        json.dump(m, f)

def refresh_challenge_db_task():
    token = get_pat()
    repos = list_org_repos(token)
    meta = ensure_metadata()
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
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
                        json.dump(json_obj, f)
                    os.replace(tmp, filename)
                    meta[name] = {
                        'sha': sha,
                        'downloaded_at': int(time.time()),
                        'path': filename
                    }
            if not readme_text:
                print("Skipped: no README")
            elif not json_obj:
                print("Skipped: no valid JSON block")
            else:
                print("Saved JSON for", name)
    save_metadata(meta)
