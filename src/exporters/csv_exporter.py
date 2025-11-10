import csv
import json
import logging
from typing import Any, Dict, Iterable, List

logger = logging.getLogger(__name__)

def _flatten_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten nested doctor record dict into a single-level dict suitable for CSV.
    Nested objects/arrays are serialized as JSON strings.
    """
    flat: Dict[str, Any] = {}

    for key, value in record.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                flat[f"{key}.{sub_key}"] = sub_val
        elif isinstance(value, list):
            flat[key] = json.dumps(value, ensure_ascii=False)
        else:
            flat[key] = value

    return flat

def _fieldnames(records: Iterable[Dict[str, Any]]) -> List[str]:
    fieldset = set()
    for rec in records:
        flat = _flatten_record(rec)
        for key in flat.keys():
            fieldset.add(key)
    return sorted(fieldset)

def export_csv(data: List[Dict[str, Any]], path: str) -> None:
    """
    Export a list of doctor dictionaries to a CSV file.
    """
    if not data:
        logger.info("No data to write to CSV. Skipping export.")
        return

    logger.info("Writing CSV output to %s", path)
    flat_records = [_flatten_record(rec) for rec in data]
    headers = _fieldnames(flat_records)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rec in flat_records:
            writer.writerow(rec)