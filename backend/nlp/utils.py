import re
import dateparser
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

def clean_title(text: str, entities: Dict[str, str]) -> str:
    """
    Remove common intent phrases and entity words from task title.
    """
    title = text.lower()

    # Remove trigger phrases
    title = re.sub(r"\b(remind me|please remind|note to self)\b", "", title)

    # Remove entity values (like Sunday, tomorrow)
    for v in entities.values():
        if v:
            title = title.replace(v.lower(), "")

    # Remove leftover filler words
    title = re.sub(r"\b(on|at|by|to)\b", "", title)

    # Clean up extra spaces + capitalize first letter
    return title.strip().capitalize() or "Untitled Task"


def parse_due_date(entities: Dict[str, str]) -> Tuple[Optional[datetime], bool]:
    """
    Parse DATE/TIME entities and detect if it's all-day.
    Returns (due_date: datetime | None, all_day: bool)

    - Uses dateparser with preference for future dates.
    - If DATE+TIME both present, parse the combined string.
    - If only DATE present and no time pattern, mark all_day = True.
    - If only TIME is present, attach to today; roll to tomorrow if that time already passed.
    """
    all_day = False
    due_date: Optional[datetime] = None

    date_str = entities.get("DATE")
    time_str = entities.get("TIME")

    settings = {"PREFER_DATES_FROM": "future"}  # prefer future dates

    # 1) If both DATE and TIME are present, parse them together
    if date_str and time_str:
        combined = f"{date_str} {time_str}"
        parsed = dateparser.parse(combined, settings=settings)
        if parsed:
            due_date = parsed
            all_day = False

    # 2) If only DATE is present
    elif date_str:
        parsed = dateparser.parse(date_str, settings=settings)
        if parsed:
            due_date = parsed
            # If no explicit time pattern in the DATE string, treat as all-day
            has_time_pattern = bool(re.search(r"\d{1,2}(:\d{2})?\s*(am|pm)?", date_str, re.I))
            if not has_time_pattern:
                all_day = True

    # 3) If only TIME is present
    elif time_str:
        parsed = dateparser.parse(time_str, settings=settings)
        if parsed:
            # If the parsed time (today at that time) is already past, roll to tomorrow
            now = datetime.now()
            if parsed < now:
                parsed = parsed + timedelta(days=1)
            due_date = parsed
            all_day = False

    # If parsed is still not None and it looks like midnight but user gave a time,
    # ensure all_day is False (defensive)
    if due_date and (time_str or (date_str and re.search(r"\d", date_str))):
        all_day = all_day and not bool(time_str)

    return due_date, all_day
