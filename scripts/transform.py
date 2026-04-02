from datetime import datetime
from config.config import FIELD_MAPPING


def _parse_date(value) -> str | None:
    """Parse Jira datetime string to date only (YYYY-MM-DD)."""
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("iso8601") or value.get("isoDate") or value.get("friendly") or str(value)
    if not isinstance(value, str):
        return str(value)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return value


def _extract_value(obj, subfield: str | None = None) -> str | None:
    """Extract a value from a field, optionally drilling into nested subfields.

    Supports dot notation for deep access, e.g. 'currentStatus.status'
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        if subfield:
            parts = subfield.split(".")
            current = obj
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return str(current) if current is not None else None
        return obj.get("value") or obj.get("name") or str(obj)
    if isinstance(obj, list):
        items = []
        for item in obj:
            if isinstance(item, dict):
                val = item.get("value") or item.get("name") or str(item)
                items.append(val)
            else:
                items.append(str(item))
        return ", ".join(items) if items else None
    return str(obj)


def _extract_numeric_suffix(key: str | None) -> str | None:
    """Extract numeric part from issue key, e.g. MURL-18273 -> 18273."""
    if not key:
        return None
    parts = key.split("-")
    return parts[-1] if len(parts) > 1 else key


def transform_record(raw: dict) -> dict:
    """Transform a single raw Jira issue into a flat dict."""
    record = {}
    fields = raw.get("fields", {})

    for key, mapping in FIELD_MAPPING.items():
        source = mapping["source"]
        value = None

        if source == "key":
            value = raw.get("key")
            if mapping.get("transform") == "numeric_suffix":
                value = _extract_numeric_suffix(value)
        elif source == "fields":
            field = mapping["field"]
            raw_value = fields.get(field)
            transform = mapping.get("transform")
            if transform == "boolean_not_null":
                value = "True" if raw_value is not None else "False"
            else:
                subfield = mapping.get("subfield")
                value = _extract_value(raw_value, subfield)
                if mapping.get("type") == "date":
                    value = _parse_date(raw_value)

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
