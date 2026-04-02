import time
import requests
from tqdm import tqdm
from config.config import JIRA_BASE_URL, JIRA_TOKEN, JIRA_REQUEST_TYPE_ID, JIRA_PAGE_LIMIT, ESTIMATED_TOTAL


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
    retries_max = 3
    pbar = None

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
                    tqdm.write(f"  Retry {attempt + 1}/{retries_max} after {wait}s: {e}")
                    time.sleep(wait)
                else:
                    raise

        data = resp.json()

        if pbar is None:
            total = limit or ESTIMATED_TOTAL
            pbar = tqdm(total=total, desc="Extracting MURLs", unit="records")

        values = data.get("values", [])
        if not values:
            break

        all_values.extend(values)
        pbar.update(len(values))

        if limit and len(all_values) >= limit:
            all_values = all_values[:limit]
            break

        if data.get("isLastPage", True):
            break

        start += JIRA_PAGE_LIMIT
        time.sleep(0.2)

    if pbar:
        pbar.close()

    print(f"Extraction complete: {len(all_values)} records")
    return all_values
