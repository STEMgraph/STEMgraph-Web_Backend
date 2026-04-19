import os

# global variables
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
