import requests
from bs4 import BeautifulSoup
from utils import logger, retry_on_exception, clean_html_text
from typing import List

class RAGEngine:
    def __init__(self):
        # We simulate browser headers to avoid basic blocks by clinic websites
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @retry_on_exception(retries=2, backoff=1)
    def fetch_website_content(self, url: str) -> str:
        """Scrapes text from the provided URL."""
        if not url.startswith('http'):
            url = 'https://' + url
            
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return self._extract_text(response.content)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape URL {url}: {e}")
            raise Exception(f"Unable to access {url}. Please verify the URL or try another.")

    def _extract_text(self, html_content: bytes) -> str:
        """Extracts and cleans visible text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "meta"]):
            script.extract()

        # Get text
        text = soup.get_text(separator=' ')
        return clean_html_text(text)

    def chunk_content(self, text: str, max_tokens_estimate: int = 4000) -> str:
        """
        Creates a temporary RAG context by taking the most relevant parts.
        Since we are using an LLM with a decent context window, we extract
        the first major portion of the site which usually contains the main info.
        For a more robust system, semantic splitting would be used here.
        """
        # Estimate: 1 token ~= 4 chars
        max_chars = max_tokens_estimate * 4
        
        if len(text) <= max_chars:
            return text
            
        # Return truncated text. In a true Vector DB RAG, we'd embed and retrieve.
        # Given constraints, we truncate for statelessness.
        logger.info("Content truncated to fit context window.")
        return text[:max_chars] + "\n...[Content Truncated]..."