import logging
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from utils.data_cleaner import clean_text

logger = logging.getLogger(__name__)

def _extract_text_lines(container: Optional[BeautifulSoup]) -> List[str]:
    if not container:
        return []
    text = container.get_text("\n")
    lines = [clean_text(line) for line in text.splitlines()]
    return [line for line in lines if line]

def parse_primary_location(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Parse the primary practice location for the doctor.
    Returns a dict with keys: name, address, city, state, zip, phone.
    """
    location: Dict[str, Any] = {
        "name": None,
        "address": None,
        "city": None,
        "state": None,
        "zip": None,
        "phone": None,
    }

    # Heuristic: use the first address-like block.
    container = None
    selectors = [
        "[data-qa-id*=location-card]",
        "[class*=location-card]",
        "[class*=practice-location]",
        "[class*=office-location]",
        "section[aria-label*=Location]",
    ]
    for sel in selectors:
        container = soup.select_one(sel)
        if container:
            break

    if not container:
        # Fallback: first address tag
        container = soup.find("address")

    if not container:
        logger.debug("No location container found.")
        return location

    lines = _extract_text_lines(container)
    if not lines:
        return location

    # Guess name as the first line, then address, then city/state/zip
    location["name"] = lines[0]

    # Find a line that looks like city/state/zip: "City, ST 12345"
    for line in lines[1:]:
        if "," in line and any(char.isdigit() for char in line):
            # Likely "City, ST 12345"
            location["address"] = " ".join(lines[1:lines.index(line)])
            city_state_zip = line
            try:
                city_part, rest = city_state_zip.split(",", 1)
                location["city"] = clean_text(city_part)
                parts = rest.strip().split()
                if parts:
                    location["state"] = parts[0]
                if len(parts) > 1:
                    location["zip"] = parts[1]
            except ValueError:
                pass
            break
    else:
        # If we can't find a city/state/zip pattern, just treat next lines as address.
        if len(lines) > 1:
            location["address"] = " ".join(lines[1:])

    # Phone number search within container
    text_full = " ".join(lines)
    for token in text_full.split():
        digits = "".join(ch for ch in token if ch.isdigit())
        if len(digits) >= 10:
            location["phone"] = token
            break

    return location

def parse_insurances(soup: BeautifulSoup) -> List[str]:
    """
    Parse accepted insurance providers from the profile page soup.
    Returns a list of insurance provider names.
    """
    insurances: List[str] = []

    # Look for a section labeled as insurance
    containers = []
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = clean_text(heading.get_text(" "))
        if not text:
            continue
        if "insurance" in text.lower() or "insurances" in text.lower():
            # The following sibling(s) likely contain the list.
            sibling = heading.find_next_sibling()
            if sibling:
                containers.append(sibling)

    if not containers:
        # Fallback: any element with class hinting at insurance
        containers = soup.select("[class*=insurance]")

    for container in containers:
        # List items first
        for li in container.find_all("li"):
            text = clean_text(li.get_text(" "))
            if text:
                insurances.append(text)
        # Fallback to delimited text
        if not container.find("li"):
            text = clean_text(container.get_text(" "))
            if text:
                for part in text.split(","):
                    p = part.strip()
                    if p:
                        insurances.append(p)

    # Deduplicate
    seen = set()
    unique: List[str] = []
    for ins in insurances:
        if ins not in seen:
            seen.add(ins)
            unique.append(ins)

    logger.debug("Parsed %d unique insurance providers.", len(unique))
    return unique