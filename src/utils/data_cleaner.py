import logging
import re
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    # Normalize whitespace
    text = re.sub(r"\s+", " ", value).strip()
    return text or None

def safe_int(value: Any) -> Optional[int]:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None

def parse_date(value: Optional[str]) -> Optional[str]:
    """
    Parse various human-friendly date strings and normalize them to MM/DD/YYYY.
    If parsing fails, returns None.
    """
    if not value:
        return None
    text = value.strip()

    # Try common patterns
    formats = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%-m/%-d/%Y") if hasattr(dt, "strftime") else dt.strftime("%m/%d/%Y")
        except ValueError:
            continue

    # As a very loose fallback, return the original string
    logger.debug("Could not parse date '%s'; returning unmodified.", value)
    return text