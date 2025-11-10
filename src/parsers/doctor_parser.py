import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils.data_cleaner import clean_text, safe_int

logger = logging.getLogger(__name__)

def _extract_name(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    """
    Attempt to extract the doctor's name from multiple possible selectors.
    """
    name_text: Optional[str] = None

    # Try common WebMD-style selectors.
    selectors = [
        "h1[data-qa-id*=doctor-name]",
        "h1[class*=doctor-name]",
        "h1[class*=provider-name]",
        "h1[itemprop=name]",
        "h1",
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el and clean_text(el.get_text()):
            name_text = clean_text(el.get_text())
            break

    if not name_text:
        return {"first": None, "last": None, "full": None}

    parts = name_text.replace("Dr.", "").replace("MD", "").strip().split()
    first = parts[0] if parts else None
    last = parts[-1] if len(parts) > 1 else None

    return {
        "first": first,
        "last": last,
        "full": name_text,
    }

def _search_label_value(soup: BeautifulSoup, label_keywords: List[str]) -> Optional[str]:
    """
    Find a value near a label like 'Gender', 'NPI', etc.
    This is heuristic-based and robust against minor HTML changes.
    """
    lowered_keywords = [kw.lower() for kw in label_keywords]

    for tag in soup.find_all(text=True):
        text = clean_text(tag)
        if not text:
            continue
        lower = text.lower()
        if any(kw in lower for kw in lowered_keywords):
            # Check siblings or parent for value.
            parent = tag.parent
            # Case: "Gender: Female"
            match = re.search(r"gender[:\s]+([A-Za-z]+)", lower)
            if match:
                return clean_text(match.group(1))

            # Try next sibling
            candidate = getattr(tag, "next_sibling", None)
            if candidate and hasattr(candidate, "get_text"):
                val = clean_text(candidate.get_text())
                if val:
                    return val
            if candidate and isinstance(candidate, str):
                val = clean_text(candidate)
                if val:
                    return val

            # Try parent text minus label text
            if parent and parent.get_text():
                text_full = clean_text(parent.get_text())
                for kw in lowered_keywords:
                    if kw in text_full.lower():
                        val = text_full.lower().replace(kw, "").replace(":", " ").strip()
                        val = clean_text(val)
                        if val:
                            return val
    return None

def _extract_gender(soup: BeautifulSoup) -> Optional[str]:
    gender = _search_label_value(soup, ["gender"])
    if not gender:
        return None
    gender = gender[0].upper()
    if gender in ("M", "F"):
        return gender
    return None

def _extract_npi(soup: BeautifulSoup) -> Optional[str]:
    # Search specific attributes first
    npi_el = soup.find(attrs={"data-npi": True})
    if npi_el:
        return clean_text(npi_el.get("data-npi"))

    # Fallback: text search
    text = clean_text(soup.get_text(" "))
    match = re.search(r"\bNPI[:\s]+(\d{8,15})\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def _extract_specialties(soup: BeautifulSoup) -> List[str]:
    specialties: List[str] = []

    # itemprop-based
    for el in soup.select("[itemprop~=medicalSpecialty]"):
        text = clean_text(el.get_text())
        if text:
            specialties.append(text)

    # Common class-based
    if not specialties:
        for el in soup.select(".specialty, .specialties, [class*=specialty]"):
            text = clean_text(el.get_text())
            if text:
                specialties.extend([t.strip() for t in text.split(",") if t.strip()])

    # Deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for sp in specialties:
        if sp not in seen:
            seen.add(sp)
            unique.append(sp)
    return unique

def _extract_degrees(soup: BeautifulSoup) -> List[str]:
    # The degree is often near the name; look for abbreviations like MD, DO, FNP-C, etc.
    name_block = soup.select_one("h1, .provider-name, .doctor-name")
    candidates: List[str] = []

    if name_block:
        text = clean_text(name_block.get_text())
        if text:
            for token in text.split(","):
                t = token.strip()
                if t and any(ch.isupper() for ch in t) and len(t) <= 10:
                    if " " not in t or "-" in t:
                        candidates.append(t)

    # Also scan chips/badges
    for el in soup.select(".degree, [class*=degree]"):
        t = clean_text(el.get_text())
        if t:
            candidates.extend([x.strip() for x in t.split(",") if x.strip()])

    seen = set()
    degrees: List[str] = []
    for d in candidates:
        if d not in seen:
            seen.add(d)
            degrees.append(d)
    return degrees

def _extract_education(soup: BeautifulSoup) -> Dict[str, Any]:
    education: Dict[str, Any] = {}
    text = clean_text(soup.get_text(" ")) or ""

    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    if year_match:
        education["graduationYear"] = safe_int(year_match.group(0))
    return education

def _extract_bio(soup: BeautifulSoup) -> Optional[str]:
    # Find a section that looks like biography
    selectors = [
        "[data-qa-id*=bio]",
        "[class*=bio]",
        "[id*=bio]",
        "section[aria-label*=Bio]",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = clean_text(el.get_text(" "))
            if text:
                return text

    # Fallback: first paragraph under main content
    main = soup.find("main") or soup.body
    if main:
        p = main.find("p")
        if p:
            text = clean_text(p.get_text(" "))
            if text and len(text.split()) > 15:
                return text
    return None

def _extract_ratings(soup: BeautifulSoup) -> Dict[str, Any]:
    ratings: Dict[str, Any] = {}

    # Look for overall rating
    overall = None
    for el in soup.select("[data-qa-id*=overall-rating], [class*=overall-rating], [class*=rating]"):
        text = clean_text(el.get_text(" "))
        if not text:
            continue
        match = re.search(r"(\d(\.\d)?)\s*/\s*5", text)
        if match:
            overall = float(match.group(1))
            break
        match = re.search(r"\b[1-5](\.\d+)?\b", text)
        if match:
            try:
                overall = float(match.group(0))
                break
            except ValueError:
                continue

    if overall is not None:
        ratings["averageRating"] = overall

    # Review count
    text = clean_text(soup.get_text(" "))
    match = re.search(r"(\d+)\s+Reviews?", text, re.IGNORECASE)
    if match:
        ratings["reviewCount"] = safe_int(match.group(1))

    return ratings

def _extract_photos(soup: BeautifulSoup) -> Optional[str]:
    # Try dedicated avatar/headshot image
    selectors = [
        "img[alt*=Doctor]",
        "img[alt*=Profile]",
        "img[class*=avatar]",
        "img[class*=headshot]",
        "img[itemprop=image]",
    ]
    for sel in selectors:
        img = soup.select_one(sel)
        if img and img.get("src"):
            return img["src"]
    return None

def _extract_urls(profile_url: str, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    urls: Dict[str, Optional[str]] = {"profile": profile_url, "appointment": None, "website": None}

    # Appointment links often contain specific phrases
    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text(" ")) or ""
        href = a["href"]
        if "appointment" in text.lower() or "book" in text.lower():
            urls["appointment"] = urljoin(profile_url, href)
        if "website" in text.lower() and not urls["website"]:
            urls["website"] = urljoin(profile_url, href)

    return urls

def _extract_provider_id(soup: BeautifulSoup, profile_url: str) -> Optional[str]:
    # Data attribute
    el = soup.find(attrs={"data-provider-id": True})
    if el:
        return clean_text(el.get("data-provider-id"))

    # Meta tag
    meta = soup.find("meta", attrs={"name": "providerid"})
    if meta and meta.get("content"):
        return clean_text(meta["content"])

    # Fallback: GUID-like substring in the HTML
    html = soup.decode()
    match = re.search(
        r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}", html, re.IGNORECASE
    )
    if match:
        return match.group(0)

    # As a last resort, use hashed URL (not ideal but deterministic)
    return None

def parse_search_results(html: str, base_url: Optional[str] = None) -> List[str]:
    """
    Parse the search results page and return a list of doctor profile URLs.
    """
    soup = BeautifulSoup(html, "lxml")
    urls: List[str] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href:
            continue

        # Heuristic: WebMD doctor profile URLs usually contain '/doctor/'.
        if "/doctor/" in href:
            full_url = urljoin(base_url, href) if base_url else href
            urls.append(full_url)

    # Deduplicate
    seen = set()
    unique: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    logger.debug("Extracted %d unique profile URLs from search results.", len(unique))
    return unique

def parse_doctor_profile(soup: BeautifulSoup, profile_url: str) -> Dict[str, Any]:
    """
    Parse a doctor profile page and return a dictionary with core doctor fields.

    Location, insurances, and reviews are parsed in their respective parser modules.
    """
    name = _extract_name(soup)
    gender = _extract_gender(soup)
    npi = _extract_npi(soup)
    specialties = _extract_specialties(soup)
    degrees = _extract_degrees(soup)
    education = _extract_education(soup)
    bio = _extract_bio(soup)
    ratings = _extract_ratings(soup)
    photos = _extract_photos(soup)
    urls = _extract_urls(profile_url, soup)
    providerid = _extract_provider_id(soup, profile_url)

    doctor: Dict[str, Any] = {
        "providerid": providerid,
        "name": name,
        "gender": gender,
        "npi": npi,
        "specialties": specialties,
        "degrees": degrees,
        "education": education,
        "photos": photos,
        "bio": bio,
        "ratings": ratings,
        "urls": urls,
    }

    logger.debug("Parsed doctor profile for %s: %s", profile_url, doctor)
    return doctor