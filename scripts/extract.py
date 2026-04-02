import json
import time
import requests
from tqdm import tqdm
from config.config import (
    JIRA_BASE_URL, JIRA_TOKEN, JIRA_REQUEST_TYPE_ID,
    JIRA_PAGE_LIMIT, ESTIMATED_TOTAL, RAW_CACHE_PATH, INPUT_DIR,
)


def _save_cache(records: list[dict]) -> None:
    """Save records to cache file."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RAW_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)


def _load_cache() -> list[dict]:
    """Load records from cache file."""
    if RAW_CACHE_PATH.exists():
        with open(RAW_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def extract_all(limit: int | None = None, resume: bool = False) -> list[dict]:
    """Extract all MURL requests from Jira Service Desk API with pagination.

    Saves progress to cache after every page. On failure, use resume=True
    to continue from where it left off.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json",
    })

    all_values = []
    if resume:
        all_values = _load_cache()
        if all_values:
            print(f"Resuming from {len(all_values)} cached records")

    url = f"{JIRA_BASE_URL}/rest/servicedeskapi/request"
    start = len(all_values)
    retries_max = 5
    total = limit or ESTIMATED_TOTAL
    pbar = tqdm(total=total, initial=start, desc="Extracting MURLs", unit="records")

    while True:
        params = {
            "requestTypeId": JIRA_REQUEST_TYPE_ID,
            "start": start,
            "limit": JIRA_PAGE_LIMIT,
            "expand": "participant,status,requestType,serviceDesk",
        }

        for attempt in range(retries_max):
            try:
                resp = session.get(url, params=params, timeout=120)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < retries_max - 1:
                    wait = 2 ** (attempt + 1)
                    tqdm.write(f"  Retry {attempt + 1}/{retries_max} after {wait}s: {e}")
                    time.sleep(wait)
                else:
                    _save_cache(all_values)
                    tqdm.write(f"  Saved {len(all_values)} records to cache before failure")
                    raise

        values = resp.json().get("values", [])
        if not values:
            break

        all_values.extend(values)
        pbar.update(len(values))
        _save_cache(all_values)

        if limit and len(all_values) >= limit:
            all_values = all_values[:limit]
            break

        if resp.json().get("isLastPage", True):
            break

        start += JIRA_PAGE_LIMIT
        time.sleep(0.2)

    pbar.close()
    _save_cache(all_values)
    print(f"Extraction complete: {len(all_values)} records")
    return all_values
