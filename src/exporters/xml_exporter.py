import logging
from typing import Any, Dict, List

import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def _dict_to_xml(parent: ET.Element, key: str, value: Any) -> None:
    if isinstance(value, dict):
        node = ET.SubElement(parent, key)
        for sub_key, sub_val in value.items():
            _dict_to_xml(node, sub_key, sub_val)
    elif isinstance(value, list):
        list_node = ET.SubElement(parent, key)
        for item in value:
            item_node = ET.SubElement(list_node, "item")
            _dict_to_xml(item_node, "value", item)
    else:
        node = ET.SubElement(parent, key)
        node.text = "" if value is None else str(value)

def export_xml(data: List[Dict[str, Any]], path: str) -> None:
    """
    Export a list of doctor dictionaries to an XML file.
    """
    logger.info("Writing XML output to %s", path)
    root = ET.Element("doctors")

    for record in data:
        doc_el = ET.SubElement(root, "doctor")
        for key, value in record.items():
            _dict_to_xml(doc_el, key, value)

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)