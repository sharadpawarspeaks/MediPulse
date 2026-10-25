import re
import socket
import ipaddress
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from app.config import Config

logger = logging.getLogger("MediPulse.RAGEngine")

class RAGEngine:
    """
    Source-Grounded Clinic & Healthcare RAG Engine.
    Hardened against SSRF (Server-Side Request Forgery) attacks,
    private IP exfiltration, cloud metadata access (169.254.169.254),
    and recursive redirect loops.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "MediPulse-Health-Verifier/2.0 (+https://github.com/sharadpawarspeaks/MediPulse)",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9",
            "Accept-Language": "en-US,en;q=0.8"
        }
        self.blocked_networks = [
            ipaddress.ip_network(net) for net in Config.BLOCKED_IP_NETWORKS
        ]

    def validate_url(self, url: str) -> str:
        """
        Validates URL scheme, hostname, and resolves DNS to ensure
        it is NOT pointing to localhost, private networks, or cloud metadata.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Prohibited URL scheme: {parsed.scheme}. Only HTTP and HTTPS are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid URL: hostname could not be resolved.")

        # Check for numeric or obvious loopback hostnames
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"):
            raise ValueError("Prohibited host: Localhost and internal metadata hosts are blocked.")

        # Resolve DNS addresses
        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        except socket.gaierror as e:
            raise ValueError(f"DNS resolution failure for host '{hostname}': {e}")

        # Check all resolved IP addresses
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                for net in self.blocked_networks:
                    if ip_obj in net:
                        raise ValueError(f"Prohibited IP address: {ip_str} resolves to blocked network {net}")
            except ValueError as ve:
                if "Prohibited IP address" in str(ve):
                    raise ve
                # Ignore unparseable IP errors
                continue

        return url

    def fetch_website_content(self, url: str, max_size_bytes: int = 4 * 1024 * 1024) -> str:
        """
        Safely fetches website content with SSRF protection, size caps, and redirect checks.
        """
        validated_url = self.validate_url(url)
        session = requests.Session()
        session.max_redirects = 4

        try:
            response = session.get(
                validated_url,
                headers=self.headers,
                timeout=Config.REQUEST_TIMEOUT,
                stream=True,
                allow_redirects=True
            )
            response.raise_for_status()

            # Verify final URL after redirects hasn't pivoted to a private address
            self.validate_url(response.url)

            # Check content type
            content_type = response.headers.get("Content-Type", "")
            if not any(t in content_type.lower() for t in ["text/html", "application/xhtml", "text/plain"]):
                raise ValueError(f"Unsupported content type '{content_type}'. Only HTML or text is supported.")

            # Read content with strict size cap
            content_chunks = []
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=16384):
                total_bytes += len(chunk)
                if total_bytes > max_size_bytes:
                    logger.warning(f"Response size exceeded {max_size_bytes} bytes; truncating.")
                    break
                content_chunks.append(chunk)

            raw_bytes = b"".join(content_chunks)
            encoding = response.encoding or "utf-8"
            return raw_bytes.decode(encoding, errors="replace")

        except requests.exceptions.RequestException as e:
            logger.error(f"Website fetch error for {url}: {e}")
            raise Exception(f"Unable to access {url}. Ensure the domain is public and reachable.")

    def extract_structured_text(self, html_content: str) -> str:
        """Extracts clean text while preserving important headings and lists."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip unneeded elements
        for element in soup(["script", "style", "nav", "footer", "meta", "noscript", "svg", "form"]):
            element.extract()

        sections: List[str] = []
        for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = tag.get_text(separator=" ").strip()
            if not text:
                continue

            # Tag headings clearly for semantic chunking
            if tag.name in ["h1", "h2", "h3"]:
                sections.append(f"\n### {text}")
            elif tag.name == "li":
                sections.append(f"- {text}")
            else:
                sections.append(text)

        cleaned_text = "\n".join(sections)
        # Collapse excessive whitespace
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        return cleaned_text.strip()

    def chunk_and_retrieve(self, text: str, query: str = "departments emergency services timings doctors insurance", top_k: int = 4) -> List[str]:
        """
        Splits text into thematic chunks and retrieves the most relevant chunks using
        a lightweight lexical BM25/keyword overlap scoring model.
        """
        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_words = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            word_count = len(para.split())
            if current_words + word_count > 350 and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_words = word_count
            else:
                current_chunk.append(para)
                current_words += word_count

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        if not chunks:
            return ["No readable content extracted from webpage."]

        # Keyword matching score
        query_terms = set(re.findall(r'\b[a-z]{3,}\b', query.lower()))
        scored_chunks = []

        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = 0
            for term in query_terms:
                if term in chunk_lower:
                    score += chunk_lower.count(term)
            scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c for score, c in scored_chunks[:top_k]]
        return top_chunks
