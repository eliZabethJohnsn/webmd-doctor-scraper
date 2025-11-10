import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

# Ensure local imports work when running as `python src/main.py`
CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from utils.request_handler import RequestHandler  # noqa: E402
from parsers.doctor_parser import parse_search_results, parse_doctor_profile  # noqa: E402
from parsers.location_parser import parse_primary_location, parse_insurances  # noqa: E402
from parsers.review_parser import parse_reviews  # noqa: E402
from exporters.json_exporter import export_json  # noqa: E402
from exporters.csv_exporter import export_csv  # noqa: E402
from exporters.xml_exporter import export_xml  # noqa: E402

def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    if not os.path.exists(path):
        logging.warning("Config file %s not found. Continuing with defaults/CLI options.", path)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error("Failed to parse config JSON: %s", e)
            return {}
    if not isinstance(data, dict):
        logging.warning("Config file must contain a JSON object at the top level.")
        return {}
    return data

def merge_config(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    # CLI args override config, config overrides defaults.
    merged = dict(config)

    if args.search_url:
        merged["searchUrl"] = args.search_url
    if args.max_items is not None:
        merged["maxItems"] = args.max_items
    if args.output_format:
        merged["outputFormat"] = args.output_format
    if args.output_file:
        merged["outputFile"] = args.output_file
    if args.proxy:
        merged.setdefault("proxyConfiguration", {})
        merged["proxyConfiguration"]["http"] = args.proxy
        merged["proxyConfiguration"]["https"] = args.proxy

    return merged

def select_exporter(fmt: str):
    fmt = fmt.lower()
    if fmt == "json":
        return export_json
    if fmt == "csv":
        return export_csv
    if fmt in ("xml", "xls", "xmls"):  # accept minor typos
        return export_xml
    raise ValueError(f"Unsupported output format: {fmt}. Use json, csv, or xml.")

def build_request_handler(config: Dict[str, Any]) -> RequestHandler:
    proxy_cfg = config.get("proxyConfiguration") or {}
    proxies = {}

    if isinstance(proxy_cfg, dict):
        for key in ("http", "https"):
            if proxy_cfg.get(key):
                proxies[key] = proxy_cfg[key]

    timeout = config.get("timeoutSeconds", 20)
    max_retries = config.get("maxRetries", 3)

    return RequestHandler(
        proxies=proxies or None,
        timeout=timeout,
        max_retries=max_retries,
    )

def scrape(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    search_url = config.get("searchUrl")
    if not search_url:
        raise ValueError("searchUrl must be provided via config or CLI arguments.")

    max_items = config.get("maxItems") or 50
    if not isinstance(max_items, int) or max_items <= 0:
        max_items = 50

    handler = build_request_handler(config)

    logging.info("Fetching search results from %s", search_url)
    search_html = handler.get(search_url)
    if search_html is None:
        raise RuntimeError("Failed to fetch search results page.")

    profile_urls = parse_search_results(search_html, base_url=search_url)
    if not profile_urls:
        logging.warning("No doctor profile URLs found in search results.")
        return []

    if len(profile_urls) > max_items:
        profile_urls = profile_urls[:max_items]

    logging.info("Found %d doctor profile URLs. Beginning profile scraping.", len(profile_urls))

    doctors: List[Dict[str, Any]] = []

    for idx, profile_url in enumerate(profile_urls, start=1):
        logging.info("(%d/%d) Fetching profile: %s", idx, len(profile_urls), profile_url)
        html = handler.get(profile_url)
        if html is None:
            logging.error("Skipping profile %s due to repeated request failures.", profile_url)
            continue

        soup = BeautifulSoup(html, "lxml")

        try:
            doctor = parse_doctor_profile(soup, profile_url)
            location = parse_primary_location(soup)
            insurances = parse_insurances(soup)
            reviews = parse_reviews(soup)

            doctor["searchUrl"] = search_url
            doctor["location"] = location
            doctor["insurances"] = insurances
            doctor["reviews"] = reviews

            doctors.append(doctor)
        except Exception as e:
            logging.exception("Error parsing doctor profile %s: %s", profile_url, e)

    logging.info("Successfully scraped %d doctor profiles.", len(doctors))
    return doctors

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="WebMD Doctor Scraper - Scrape doctor details from WebMD search results."
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to JSON config file (default: config/settings.example.json if present).",
    )
    parser.add_argument(
        "--search-url",
        help="WebMD doctor search URL to scrape.",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        help="Maximum number of doctor profiles to scrape.",
    )
    parser.add_argument(
        "--output-format",
        "-f",
        choices=["json", "csv", "xml"],
        help="Output format (json, csv, or xml).",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        help="Path to output file. Defaults to ./data/sample_output.<ext> based on format.",
    )
    parser.add_argument(
        "--proxy",
        help="Optional HTTP/HTTPS proxy URL. Applies to both http and https.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO.",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    default_config_path = args.config or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.example.json"
    )

    config = load_config(default_config_path)
    config = merge_config(config, args)

    output_format = (config.get("outputFormat") or "json").lower()
    try:
        exporter = select_exporter(output_format)
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)

    output_file = config.get("outputFile")
    if not output_file:
        ext = output_format
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(base_dir, exist_ok=True)
        output_file = os.path.join(base_dir, f"sample_output.{ext}")
        config["outputFile"] = output_file

    try:
        doctors = scrape(config)
    except Exception as e:
        logging.exception("Scraping failed: %s", e)
        sys.exit(1)

    if not doctors:
        logging.warning("No doctor data to export. Exiting without writing output.")
        return

    try:
        exporter(doctors, output_file)
        logging.info("Exported %d records to %s", len(doctors), output_file)
    except Exception as e:
        logging.exception("Failed to export data: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()