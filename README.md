# MURL Data Pipeline

Extracts MURL (Marketing URL) data from Jira Service Desk, stores it in DuckDB/Parquet, and generates an XLSX report.

Replaces the internal MURL Dashboard which is being decommissioned.

## Architecture

```
Jira Service Desk API
        |
        v
   input/raw_extract.json     (raw API response cache)
        |
        v
   output/murl.duckdb          (analytical database)
   output/murl.parquet          (columnar export)
   output/murl_report.xlsx      (Excel report with filters)
```

## Setup

```bash
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env with your Jira Personal Access Token
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JIRA_BASE_URL` | Jira instance URL | `https://your-jira-instance.example.com` |
| `JIRA_TOKEN` | Personal Access Token | - |
| `INPUT_DIR` | Directory for raw API data | `./input` |
| `OUTPUT_DIR` | Directory for processed output | `./output` |

## Usage

```bash
# Full pipeline (extract + transform + load + report)
python main.py

# Test run with limited records
python main.py --limit 5

# Run individual steps
python main.py --step extract       # Only fetch from Jira API
python main.py --step transform     # Only transform cached data
python main.py --step load          # Transform + load to DuckDB/Parquet
python main.py --step report        # Generate XLSX from existing DuckDB
```

## Project Structure

```
MURL/
├── config/
│   ├── config.py           # Settings, field mapping, API config
│   └── .env.example        # Environment template
├── scripts/
│   ├── extract.py          # Jira API extraction (paginated, ~18k records)
│   ├── transform.py        # Raw JSON to flat dicts
│   ├── load.py             # DuckDB + Parquet writer
│   └── report.py           # XLSX report generator
├── input/                  # Raw API response cache
├── output/                 # DuckDB, Parquet, XLSX
├── main.py                 # CLI entry point
└── requirements.txt
```

## Data Source

- **API**: `/rest/servicedeskapi/request?requestTypeId=321`
- **Portal ID**: 11
- **Records**: ~18,000

## Report Columns

ID, MURL Name, Target URLs (Default + 10 languages), Is Tiny URL, Requester, Requested For, Created, MURL Validity, Due Date/Time, Owner 1/2, Status, Business Division, Domain, Activation, Communication, Region, Purpose.

## Notes

- The field mapping in `config/config.py` is based on screenshots of the API response and needs validation after the first real run.
- The `.env` file must be placed in `config/` (not project root).
- Runs on the corporate machine where Jira is accessible.
