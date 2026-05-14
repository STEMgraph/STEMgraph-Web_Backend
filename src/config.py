import os

# ============================================================
# Environment Variables (zentral konfiguriert)
# ============================================================

# GitHub API
GITHUB_ORG = os.environ['GITHUB_ORG']
GITHUB_PAT = os.environ['GITHUB_PAT']

# Directories
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/graph-db/repos')
TEMPLATE_DIR = os.environ.get('TEMPLATE_DIR', '/graph-db/templates')
DATABASE_DIR = os.environ.get('DATABASE_DIR', '/graph-db')
LOG_DIR = os.environ.get('LOG_DIR', '/graph-db/logs')

# Logging
LOG_DB_PATH = os.environ.get('LOG_DB_PATH', os.path.join(LOG_DIR, 'log.db'))
LOG_CONSOLE = os.environ.get('LOG_CONSOLE', 'false').lower() == 'true'
MAX_LOG_SIZE_MB = int(os.environ.get('MAX_LOG_SIZE_MB', '50'))
MAX_LOG_AGE_DAYS = int(os.environ.get('MAX_LOG_AGE_DAYS', '30'))

# ============================================================
# Derived Paths (berechnete Pfade)
# ============================================================

METADATA_FILE = os.path.join(STORAGE_DIR, 'metadata.json')
LD_CONTEXT_TEMPLATE = os.path.join(TEMPLATE_DIR, 'ld-context.json')
LD_METADATA_TEMPLATE = os.path.join(TEMPLATE_DIR, 'ld-metadata.json')
LD_DATABASE = os.path.join(DATABASE_DIR, 'ld-database.json')

# Aliases für Rückwärtskompatibilität
ORG = GITHUB_ORG
