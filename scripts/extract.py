import json
import time
import requests
from tqdm import tqdm
from config.config import (
    JIRA_BASE_URL, JIRA_TOKEN, JIRA_JQL,
    JIRA_PAGE_LIMIT, RAW_CACHE_PATH, INPUT_DIR,
)


def _count_cached() -> int:
    """Count lines in JSONL cache."""
    if not RAW_CACHE_PATH.exists():
        return 0
    with open(RAW_CACHE_PATH, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def _append_cache(records: list[dict]) -> None:
    """Append records to JSONL cache (one JSON object per line)."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RAW_CACHE_PATH, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_cache() -> list[dict]:
    """Load all records from JSONL cache."""
    if not RAW_CACHE_PATH.exists():
        return []
    records = []
    with open(RAW_CACHE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_all(limit: int | None = None, resume: bool = False) -> list[dict]:
    """Extract all MURL issues via Jira REST API with JQL.

    Uses /rest/api/2/search with JQL for precise filtering.
    Appends each page to a JSONL cache.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json",
    })

    cached_count = 0
    if resume:
        cached_count = _count_cached()
        if cached_count:
            print(f"Resuming from {cached_count} cached records")
    else:
        if RAW_CACHE_PATH.exists():
            RAW_CACHE_PATH.unlink()

    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    start = cached_count
    fetched = 0
    retries_max = 5
    total = None
    pbar = None

    while True:
        params = {
            "jql": JIRA_JQL,
            "startAt": start,
            "maxResults": JIRA_PAGE_LIMIT,
        }

        for attempt in range(retries_max):
            try:
                resp = session.get(url, params=params, timeout=120)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < retries_max - 1:
                    wait = 2 ** (attempt + 1)
                    if pbar:
                        tqdm.write(f"  Retry {attempt + 1}/{retries_max} after {wait}s: {e}")
                    time.sleep(wait)
                else:
                    raise

        data = resp.json()

        if pbar is None:
            total = data.get("total", 0)
            effective_total = min(limit, total) if limit else total
            pbar = tqdm(total=effective_total, initial=start, desc="Extracting MURLs", unit="records")

        issues = data.get("issues", [])
        if not issues:
            break

        _append_cache(issues)
        fetched += len(issues)
        pbar.update(len(issues))

        if limit and (cached_count + fetched) >= limit:
            break

        if (start + len(issues)) >= total:
            break

        start += JIRA_PAGE_LIMIT
        time.sleep(0.2)

    if pbar:
        pbar.close()

    total_records = cached_count + fetched
    print(f"Extraction complete: {total_records} records")
    return load_cache()[:limit] if limit else load_cache()
