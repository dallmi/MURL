from datetime import datetime
from config.config import FIELD_MAPPING


def _get_request_field_value(request_field_values: list[dict], field_id: str, subfield: str | None = None) -> str | None:
    """Extract a value from requestFieldValues by fieldId."""
    for field in request_field_values:
        if field.get("fieldId") == field_id:
            value = field.get("value")
            if value is None:
                return None
            if isinstance(value, dict):
                if subfield:
                    return value.get(subfield)
                return value.get("value") or value.get("name") or str(value)
            if isinstance(value, list):
                parts = []
                for item in value:
                    if isinstance(item, dict):
                        parts.append(item.get("value") or item.get("name") or str(item))
                    else:
                        parts.append(str(item))
                return ", ".join(parts) if parts else None
            return str(value)
    return None


def _parse_datetime(value: str | None) -> str | None:
    """Parse Jira datetime string to ISO format."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return value


def transform_record(raw: dict) -> dict:
    """Transform a single raw Jira record into a flat dict."""
    record = {}
    request_fields = raw.get("requestFieldValues", [])

    for key, mapping in FIELD_MAPPING.items():
        path = mapping["path"]
        value = None

        if path == "issueKey":
            value = raw.get("issueKey")

        elif path == "createdDate":
            value = _parse_datetime(raw.get("createdDate"))

        elif path == "reporter":
            reporter = raw.get("reporter", {})
            value = reporter.get(mapping.get("subfield", "displayName"))

        elif path == "currentStatus":
            status = raw.get("currentStatus", {})
            value = status.get(mapping.get("subfield", "status"))

        elif path == "requestFieldValues":
            field_id = mapping.get("field_id", "")
            subfield = mapping.get("subfield")
            value = _get_request_field_value(request_fields, field_id, subfield)
            if mapping.get("type") == "datetime":
                value = _parse_datetime(value)

        record[key] = value

    return record


def transform_all(raw_records: list[dict]) -> list[dict]:
    """Transform all raw records."""
    transformed = []
    for raw in raw_records:
        try:
            transformed.append(transform_record(raw))
        except Exception as e:
            issue_key = raw.get("issueKey", "UNKNOWN")
            print(f"  Warning: Failed to transform {issue_key}: {e}")
    print(f"Transformed {len(transformed)} of {len(raw_records)} records")
    return transformed
