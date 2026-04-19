import os, re, json, time, base64, requests
from config import GITHUB_PAT, ORG, STORAGE_DIR, METADATA_FILE
from services.graph_ld import createdb_jsonld
from services.graph_nl import createdb_jsonnl   # veraltet


# auxiliary functions to build / update the database cache

def get_pat():
    return GITHUB_PAT

def list_org_repos(token):
    url = f'https://api.github.com/orgs/{ORG}/repos?per_page=100'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    repos = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
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
