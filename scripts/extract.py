import time
import requests
from config.config import JIRA_BASE_URL, JIRA_TOKEN, JIRA_REQUEST_TYPE_ID, JIRA_PAGE_LIMIT


def extract_all(limit: int | None = None) -> list[dict]:
    """Extract all MURL requests from Jira Service Desk API with pagination."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json",
    })

    url = f"{JIRA_BASE_URL}/rest/servicedeskapi/request"
    all_values = []
    start = 0
    total = None
    retries_max = 3

    while True:
        params = {
            "requestTypeId": JIRA_REQUEST_TYPE_ID,
            "start": start,
            "limit": JIRA_PAGE_LIMIT,
            "expand": "participant,status,requestType,serviceDesk",
        }

        for attempt in range(retries_max):
            try:
                resp = session.get(url, params=params, timeout=30)
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < retries_max - 1:
                    wait = 2 ** (attempt + 1)
                    print(f"  Retry {attempt + 1}/{retries_max} after {wait}s: {e}")
                    time.sleep(wait)
                else:
                    raise

        data = resp.json()

        if total is None:
            total = data.get("size", 0)
            print(f"Total records: {total}")

        values = data.get("values", [])
        if not values:
            break

        all_values.extend(values)
        fetched = len(all_values)
        print(f"  Fetched {fetched}/{total}")

        if limit and fetched >= limit:
            all_values = all_values[:limit]
            break

        if data.get("isLastPage", True):
            break

        start += JIRA_PAGE_LIMIT
        time.sleep(0.2)

    print(f"Extraction complete: {len(all_values)} records")
    return all_values
