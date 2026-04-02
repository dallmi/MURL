from datetime import datetime
from config.config import FIELD_MAPPING


def _parse_datetime(value) -> str | None:
    """Parse Jira datetime string or dict to ISO format."""
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("iso8601") or value.get("isoDate") or value.get("friendly") or str(value)
    if not isinstance(value, str):
        return str(value)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return value


def _extract_value(obj, subfield: str | None = None) -> str | None:
    """Extract a value from a field, optionally drilling into a subfield."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        if subfield:
            return obj.get(subfield)
        return obj.get("value") or obj.get("name") or str(obj)
    if isinstance(obj, list):
        parts = []
        for item in obj:
            if isinstance(item, dict):
                val = item.get("value") or item.get("name") or str(item)
                parts.append(val)
            else:
                parts.append(str(item))
        return ", ".join(parts) if parts else None
    return str(obj)


def transform_record(raw: dict) -> dict:
    """Transform a single raw Jira issue into a flat dict."""
    record = {}
    fields = raw.get("fields", {})

    for key, mapping in FIELD_MAPPING.items():
        source = mapping["source"]
        value = None

        if source == "key":
            value = raw.get("key")
        elif source == "fields":
            field = mapping["field"]
            raw_value = fields.get(field)
            subfield = mapping.get("subfield")
            value = _extract_value(raw_value, subfield)
            if mapping.get("type") == "datetime":
                value = _parse_datetime(raw_value)

        record[key] = value

    return record


def transform_all(raw_records: list[dict]) -> list[dict]:
    """Transform all raw records."""
    transformed = []
    for raw in raw_records:
        try:
            transformed.append(transform_record(raw))
        except Exception as e:
            issue_key = raw.get("key", "UNKNOWN")
            print(f"  Warning: Failed to transform {issue_key}: {e}")
    print(f"Transformed {len(transformed)} of {len(raw_records)} records")
    return transformed
