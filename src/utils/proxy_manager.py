thonimport logging

class ProxyManager:
    def __init__(self, proxy_config):
        self.proxy_config = proxy_config

    def get_proxy(self):
        if not self.proxy_config:
            logging.info("No proxy configuration provided.")
            return None
        proxy_url = self.proxy_config.get("url")
        if proxy_url:
            logging.info(f"Using proxy: {proxy_url}")
            return {"http": proxy_url, "https": proxy_url}
        return None