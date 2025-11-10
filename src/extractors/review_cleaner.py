thonfrom bs4 import BeautifulSoup

def clean_reviews(soup: BeautifulSoup):
    reviews = []
    for div in soup.select(".review"):
        text = div.get_text(strip=True)
        rating_el = div.select_one(".rating")
        rating = rating_el.get("data-rating") if rating_el else None
        reviews.append({"text": text, "rating": rating})
    return reviews