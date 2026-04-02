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
FIELD_MAPPING = {
    "issue_key": {"source": "key"},
    "summary": {"source": "fields", "field": "summary"},
    "murl_name": {"source": "fields", "field": "customfield_13721"},
    "default_target_url": {"source": "fields", "field": "customfield_13710"},
    "target_german": {"source": "fields", "field": "customfield_13711"},
    "target_french": {"source": "fields", "field": "customfield_13713"},
    "target_spanish": {"source": "fields", "field": "customfield_13714"},
    "target_portuguese": {"source": "fields", "field": "customfield_13715"},
    "target_russian": {"source": "fields", "field": "customfield_13716"},
    "target_japanese": {"source": "fields", "field": "customfield_13717"},
    "target_korean": {"source": "fields", "field": "customfield_13718"},
    "target_dutch": {"source": "fields", "field": "customfield_13801"},
    "target_simplified_chinese": {"source": "fields", "field": "customfield_13719"},
    "target_traditional_chinese": {"source": "fields", "field": "customfield_13720"},
    "is_tiny_url": {"source": "fields", "field": "customfield_14300", "subfield": "value"},
    "reporter": {"source": "fields", "field": "reporter", "subfield": "displayName"},
    "reporter_email": {"source": "fields", "field": "reporter", "subfield": "emailAddress"},
    "creator": {"source": "fields", "field": "creator", "subfield": "displayName"},
    "assignee": {"source": "fields", "field": "assignee", "subfield": "displayName"},
    "created": {"source": "fields", "field": "created", "type": "datetime"},
    "updated": {"source": "fields", "field": "updated", "type": "datetime"},
    "status": {"source": "fields", "field": "status", "subfield": "name"},
    "description": {"source": "fields", "field": "description"},
    "murl_validity": {"source": "fields", "field": "customfield_13724", "subfield": "value"},
    "due_date_time": {"source": "fields", "field": "customfield_13708"},
    "owner_1": {"source": "fields", "field": "customfield_13705", "subfield": "displayName"},
    "owner_2": {"source": "fields", "field": "customfield_13706", "subfield": "displayName"},
    "business_division": {"source": "fields", "field": "customfield_10019", "subfield": "value"},
    "domain": {"source": "fields", "field": "customfield_13707", "subfield": "value"},
    "activation": {"source": "fields", "field": "customfield_13702", "subfield": "value"},
    "communication": {"source": "fields", "field": "customfield_13722", "subfield": "value"},
    "region": {"source": "fields", "field": "customfield_13725", "subfield": "value"},
    "requested_for": {"source": "fields", "field": "customfield_10603", "subfield": "displayName"},
    "language_selection": {"source": "fields", "field": "customfield_13709", "subfield": "value"},
}

XLSX_COLUMNS = [
    ("ID", "issue_key"),
    ("Summary", "summary"),
    ("MURL Name", "murl_name"),
    ("Default Target URL", "default_target_url"),
    ("Target German", "target_german"),
    ("Target French", "target_french"),
    ("Target Spanish", "target_spanish"),
    ("Target Portuguese", "target_portuguese"),
    ("Target Russian", "target_russian"),
    ("Target Japanese", "target_japanese"),
    ("Target Korean", "target_korean"),
    ("Target Dutch", "target_dutch"),
    ("Target Simplified Chinese", "target_simplified_chinese"),
    ("Target Traditional Chinese", "target_traditional_chinese"),
    ("Is Tiny URL", "is_tiny_url"),
    ("Reporter", "reporter"),
    ("Reporter Email", "reporter_email"),
    ("Creator", "creator"),
    ("Assignee", "assignee"),
    ("Requested For", "requested_for"),
    ("Created", "created"),
    ("Updated", "updated"),
    ("MURL Validity", "murl_validity"),
    ("Due Date/Time", "due_date_time"),
    ("Owner 1", "owner_1"),
    ("Owner 2", "owner_2"),
    ("Status", "status"),
    ("Business Division", "business_division"),
    ("Domain", "domain"),
    ("Activation", "activation"),
    ("Communication", "communication"),
    ("Region", "region"),
    ("Description", "description"),
]
