# constants/__init__.py
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
DBT_PROJECT_DIR = PROJECT_ROOT / "dagster_duck_models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DBT_PROJECT_DIR.mkdir(exist_ok=True)

# File paths
DUCKDB_PATH = DATA_DIR / "duck_pond.duckdb"
DBT_MANIFEST_PATH = DBT_PROJECT_DIR / "target" / "manifest.json"