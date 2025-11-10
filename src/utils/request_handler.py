import logging
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

class RequestHandler:
    """
    Thin wrapper around requests.Session with retry and proxy support.
    """

    def __init__(
        self,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 20,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        user_agent: Optional[str] = None,
    ) -> None:
        self.session = requests.Session()
        self.proxies = proxies or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )

        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
        )

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Perform a GET request with retries.
        Returns response text on success, or None on repeated failure.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    "Requesting %s (attempt %d/%d)", url, attempt, self.max_retries
                )
                response = self.session.get(
                    url,
                    params=params,
                    proxies=self.proxies or None,
                    timeout=self.timeout,
                )
                if response.status_code >= 400:
                    logger.warning(
                        "Received HTTP %s for %s", response.status_code, url
                    )
                    if 400 <= response.status_code < 500:
                        # Client errors are usually unrecoverable
                        break
                response.raise_for_status()
                return response.text
            except Exception as e:
                last_exception = e
                wait_time = self.backoff_factor * attempt
                logger.warning(
                    "Request to %s failed on attempt %d/%d: %s. Retrying in %.1fs...",
                    url,
                    attempt,
                    self.max_retries,
                    e,
                    wait_time,
                )
                time.sleep(wait_time)

        logger.error("Failed to fetch %s after %d attempts: %s", url, self.max_retries, last_exception)
        return None