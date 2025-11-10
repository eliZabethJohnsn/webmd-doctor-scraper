import logging
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from utils.data_cleaner import clean_text, parse_date

logger = logging.getLogger(__name__)

def _extract_rating(block: BeautifulSoup) -> Optional[str]:
    # Look for numeric rating within the block.
    # Common pattern: "5.0" or "5 stars"
    text = clean_text(block.get_text(" "))
    if not text:
        return None

    for token in text.split():
        token_clean = token.strip().rstrip("★")
        if token_clean.replace(".", "", 1).isdigit():
            try:
                value = float(token_clean)
                if 1.0 <= value <= 5.0:
                    return str(value)
            except ValueError:
                continue
    return None

def _extract_text(block: BeautifulSoup) -> Optional[str]:
    # Prefer paragraph-level text.
    paragraphs = block.find_all("p")
    if paragraphs:
        texts = [clean_text(p.get_text(" ")) for p in paragraphs]
        texts = [t for t in texts if t]
        if texts:
            return " ".join(texts)

    text = clean_text(block.get_text(" "))
    if text and len(text.split()) > 5:
        return text
    return None

def _extract_date(block: BeautifulSoup) -> Optional[str]:
    # Look for a small, muted, or date-like span
    for el in block.find_all(["span", "time"]):
        text = clean_text(el.get_text(" "))
        if not text:
            continue
        parsed = parse_date(text)
        if parsed:
            return parsed
    return None

def parse_reviews(soup: BeautifulSoup, max_reviews: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Parse an array of patient reviews from the profile page soup.
    Returns a list of dicts with fields: rating, text, date.
    """
    reviews: List[Dict[str, Any]] = []

    # Try to find containers that look like review blocks.
    candidates = soup.select("[class*=review]")
    if not candidates:
        # Fallback: guesses
        candidates = soup.find_all("article")

    for block in candidates:
        text = _extract_text(block)
        if not text:
            continue

        rating = _extract_rating(block)
        date_str = _extract_date(block)

        review: Dict[str, Any] = {
            "rating": rating,
            "text": text,
            "date": date_str,
        }
        reviews.append(review)

        if max_reviews is not None and len(reviews) >= max_reviews:
            break

    logger.debug("Parsed %d reviews from profile page.", len(reviews))
    return reviews