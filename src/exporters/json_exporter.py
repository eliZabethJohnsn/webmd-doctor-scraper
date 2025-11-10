import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def export_json(data: List[Dict[str, Any]], path: str) -> None:
    """
    Export a list of doctor dictionaries to a JSON file.
    """
    logger.info("Writing JSON output to %s", path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)