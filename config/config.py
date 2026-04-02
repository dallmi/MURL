import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://your-jira-instance.example.com")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
INPUT_DIR = Path(os.getenv("INPUT_DIR", "./input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

JIRA_REQUEST_TYPE_ID = 321
JIRA_PORTAL_ID = 11
JIRA_PAGE_LIMIT = 100
ESTIMATED_TOTAL = 18116

RAW_CACHE_PATH = INPUT_DIR / "raw_extract.jsonl"
DUCKDB_PATH = OUTPUT_DIR / "murl.duckdb"
PARQUET_PATH = OUTPUT_DIR / "murl.parquet"
XLSX_PATH = OUTPUT_DIR / "murl_report.xlsx"

FIELD_MAPPING = {
    "issue_key": {"path": "issueKey"},
    "murl_name": {"path": "requestFieldValues", "field_id": "customfield_13721", "label": "MURL name"},
    "default_target_url": {"path": "requestFieldValues", "field_id": "customfield_13710", "label": "Default target URL"},
    "target_german": {"path": "requestFieldValues", "field_id": "customfield_13711", "label": "Target German"},
    "target_french": {"path": "requestFieldValues", "field_id": "customfield_13713", "label": "Target French"},
    "target_spanish": {"path": "requestFieldValues", "field_id": "customfield_13714", "label": "Target Spanish"},
    "target_portuguese": {"path": "requestFieldValues", "field_id": "customfield_13715", "label": "Target Portuguese"},
    "target_russian": {"path": "requestFieldValues", "field_id": "customfield_13716", "label": "Target Russian"},
    "target_japanese": {"path": "requestFieldValues", "field_id": "customfield_13717", "label": "Target Japanese"},
    "target_korean": {"path": "requestFieldValues", "field_id": "customfield_13718", "label": "Target Korean"},
    "target_dutch": {"path": "requestFieldValues", "field_id": "customfield_18001", "label": "Target Dutch"},
    "target_simplified_chinese": {"path": "requestFieldValues", "field_id": "customfield_13719", "label": "Target Simplified Chinese"},
    "target_traditional_chinese": {"path": "requestFieldValues", "field_id": "customfield_13720", "label": "Target Traditional Chinese"},
    "is_tiny_url": {"path": "requestFieldValues", "field_id": "customfield_14300", "label": "Create a Tiny Marketing URL"},
    "requester": {"path": "reporter", "subfield": "displayName"},
    "requester_email": {"path": "reporter", "subfield": "emailAddress"},
    "requested_for": {"path": "requestFieldValues", "field_id": "customfield_10603", "label": "Requested for", "subfield": "displayName"},
    "created": {"path": "createdDate", "type": "datetime"},
    "murl_validity": {"path": "requestFieldValues", "field_id": "customfield_13724", "label": "MURL validity"},
    "due_date_time": {"path": "requestFieldValues", "field_id": "customfield_13708", "label": "Due date/time"},
    "owner_1": {"path": "requestFieldValues", "field_id": "customfield_13705", "label": "Owner 1", "subfield": "displayName"},
    "owner_2": {"path": "requestFieldValues", "field_id": "customfield_13706", "label": "Owner 2", "subfield": "displayName"},
    "status": {"path": "currentStatus", "subfield": "status"},
    "business_division": {"path": "requestFieldValues", "field_id": "customfield_10019", "label": "Business Division requested for"},
    "domain": {"path": "requestFieldValues", "field_id": "customfield_13707", "label": "Domain"},
    "activation": {"path": "requestFieldValues", "field_id": "customfield_13702", "label": "Activation"},
    "communication": {"path": "requestFieldValues", "field_id": "customfield_13722", "label": "Communication"},
    "region": {"path": "requestFieldValues", "field_id": "customfield_13725", "label": "Region(s)"},
    "purpose": {"path": "requestFieldValues", "field_id": "description", "label": "Purpose"},
    "language_selection": {"path": "requestFieldValues", "field_id": "customfield_13709", "label": "Language selection"},
    "properties": {"path": "requestFieldValues", "field_id": "customfield_13709b", "label": "Properties"},
}

XLSX_COLUMNS = [
    ("ID", "issue_key"),
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
    ("Requester", "requester"),
    ("Requester Email", "requester_email"),
    ("Requested For", "requested_for"),
    ("Created", "created"),
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
    ("Purpose", "purpose"),
]
