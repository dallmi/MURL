import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://your-jira-instance.example.com")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
INPUT_DIR = Path(os.getenv("INPUT_DIR", "./input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

JIRA_JQL = "project = MURL"
JIRA_PAGE_LIMIT = 100

RAW_CACHE_PATH = INPUT_DIR / "raw_extract.jsonl"
DUCKDB_PATH = OUTPUT_DIR / "murl.duckdb"
PARQUET_PATH = OUTPUT_DIR / "murl.parquet"
XLSX_PATH = OUTPUT_DIR / "murl_report.xlsx"

# JQL API: fields are directly under issues[].fields.customfield_XXXXX
# "field" = customfield ID, "subfield" = nested key for objects (e.g. displayName)
# "type": "date" = DD.MM.YYYY HH:MM:SS format
FIELD_MAPPING = {
    "id": {"source": "key", "transform": "numeric_suffix"},
    "murl_name": {"source": "fields", "field": "customfield_13721"},
    "target_url": {"source": "fields", "field": "customfield_13732"},
    "is_tiny_url": {"source": "fields", "field": "customfield_14300", "transform": "boolean_not_null"},
    "requestor": {"source": "fields", "field": "creator", "subfield": "displayName"},
    "created": {"source": "fields", "field": "created", "type": "date"},
    "updated": {"source": "fields", "field": "updated", "type": "date"},
    "expiration": {"source": "fields", "field": "customfield_13724", "subfield": "value"},
    "owner_1": {"source": "fields", "field": "customfield_13705", "subfield": "displayName"},
    "owner_2": {"source": "fields", "field": "customfield_13706", "subfield": "displayName"},
    "status": {"source": "fields", "field": "customfield_10001", "subfield": "currentStatus.status"},
    "activation": {"source": "fields", "field": "customfield_13702", "subfield": "value"},
    "domain": {"source": "fields", "field": "customfield_13707", "subfield": "value"},
    "business_division": {"source": "fields", "field": "customfield_10019", "subfield": "value"},
    "region": {"source": "fields", "field": "customfield_13725", "subfield": "value"},
    "description": {"source": "fields", "field": "description"},
}

XLSX_COLUMNS = [
    ("ID", "id"),
    ("MURL Name", "murl_name"),
    ("Target URL", "target_url"),
    ("Is Tiny URL", "is_tiny_url"),
    ("Requestor", "requestor"),
    ("Created", "created"),
    ("Updated", "updated"),
    ("Expiration", "expiration"),
    ("Owner 1", "owner_1"),
    ("Owner 2", "owner_2"),
    ("Status", "status"),
    ("Activation", "activation"),
    ("Domain", "domain"),
    ("Business Division", "business_division"),
    ("Region", "region"),
    ("Description", "description"),
]
