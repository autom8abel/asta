from typing import Dict, Optional
import dateparser

def parse_due_date(entities: Dict[str, str]) -> Optional[str]:
    """
    Convert NLP-extracted DATE/TIME entities into a proper datetime string.
    Returns ISO8601 string (e.g., '2025-09-18T17:00:00') or None if parsing fails.
    """
    date_str = entities.get("DATE")
    time_str = entities.get("TIME")

    if date_str and time_str:
        combined = f"{date_str} {time_str}"
    elif date_str:
        combined = date_str
    elif time_str:
        combined = time_str
    else:
        return None

    parsed = dateparser.parse(combined)
    if parsed:
        return parsed.isoformat()
    return None
