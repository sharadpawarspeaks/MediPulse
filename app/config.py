import os
import secrets
from dotenv import load_dotenv

# Force reload local environment variables from .env
load_dotenv(dotenv_path=".env", override=True)

class Config:
    PROJECT_NAME = "MediPulse"
    TAGLINE = "Understand health information. Find evidence. Make informed next steps."
    VERSION = "2.0.0"

    # Security & Flask Secret
    SECRET_KEY = (os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY") or secrets.token_hex(32)).strip("\"' \t\r\n")
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 6 MB max request/upload size
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))

    # AI Model Configuration (Google Gemma as primary model)
    GEMINI_API_KEY = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GEMMA_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("APIM_API_KEY")
        or ""
    ).strip("\"' \t\r\n")

    GEMMA_MODEL = (
        os.getenv("GEMMA_MODEL")
        or os.getenv("GEMMA_MODEL_NAME")
        or "gemma-4-26b-a4b-it"
    ).strip("\"' \t\r\n")

    GEMMA_ENDPOINT = (
        os.getenv("GEMMA_ENDPOINT")
        or os.getenv("APIM_ENDPOINT")
        or ""
    ).strip("\"' \t\r\n")

    # Tavily API Key for live medical authority web search
    TAVILY_API_KEY = (
        os.getenv("TAVILY_API_KEY")
        or ""
    ).strip("\"' \t\r\n")

    # Mock mode flag: active if explicit or if neither key nor endpoint is set
    MOCK_AI = os.getenv("MOCK_AI", "").lower() in ("true", "1", "yes") or not bool(GEMINI_API_KEY or GEMMA_ENDPOINT)

    # Trusted Health Authority Domains Whitelist for Evidence Retrieval
    TRUSTED_HEALTH_DOMAINS = [
        "who.int",
        "cdc.gov",
        "nih.gov",
        "ncbi.nlm.nih.gov",
        "medlineplus.gov",
        "nhs.uk",
        "mayoclinic.org",
        "hopkinsmedicine.org",
        "icmr.gov.in",
        "aiims.edu",
        "mohfw.gov.in"
    ]

    # Blocked IP Networks for SSRF Defense in Clinic RAG
    BLOCKED_IP_NETWORKS = [
        "0.0.0.0/8",
        "10.0.0.0/8",
        "127.0.0.0/8",
        "169.254.0.0/16",      # Link-local & AWS/GCP metadata (169.254.169.254)
        "172.16.0.0/12",
        "192.168.0.0/16",
        "100.64.0.0/10",      # Carrier NAT
        "198.18.0.0/15",      # Benchmark
        "224.0.0.0/4",        # Multicast
        "240.0.0.0/4",        # Reserved
        "::1/128",            # IPv6 Loopback
        "fc00::/7",           # IPv6 Unique Local
        "fe80::/10",          # IPv6 Link Local
    ]
