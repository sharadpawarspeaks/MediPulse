import json
import re
import logging
from typing import Callable, Any, Dict
from functools import wraps
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MediPulse-Utils")

def append_disclaimer(content: str) -> str:
    """Appends the mandatory medical disclaimer to AI responses."""
    disclaimer = (
        "\n\n---\n"
        "**⚠️ IMPORTANT DISCLAIMER:**\n"
        "This application is only for health awareness and educational purposes. "
        "It is NOT a replacement for professional medical advice, diagnosis or treatment. "
        "Always consult a qualified healthcare professional."
    )
    if "IMPORTANT DISCLAIMER" not in content:
        return content + disclaimer
    return content

def extract_json(text: str) -> Dict[str, Any]:
    """Safely extracts JSON from LLM outputs, handling markdown formatting."""
    text = text.strip()
    # Try to find JSON block wrapped in markdown
    match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parsing Error: {e}")
        # Graceful fallback structure
        return {
            "content": "An error occurred while formatting the response. Please try again.",
            "confidence": "Low",
            "follow_up_questions": [],
            "sources": []
        }

def retry_on_exception(retries: int = 3, backoff: int = 2) -> Callable:
    """Decorator to retry a function upon exception."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    logger.warning(f"Attempt {attempt}/{retries} failed for {func.__name__}: {e}")
                    if attempt >= retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries.")
                        raise e
                    time.sleep(backoff)
        return wrapper
    return decorator

def clean_html_text(html_text: str) -> str:
    """Basic text cleanup for scraped HTML text."""
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', html_text)
    return text.strip()