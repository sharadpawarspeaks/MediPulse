import json
import re
import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MediPulse.Utils")

def append_disclaimer(content: str) -> str:
    """Appends standard medical disclaimer to text if not present."""
    disclaimer = (
        "\n\n---\n"
        "**⚠️ IMPORTANT DISCLAIMER:**\n"
        "This application is strictly for health awareness and educational purposes. "
        "It is NOT a replacement for professional clinical judgment, diagnosis, or treatment. "
        "Always consult a licensed physician for healthcare concerns."
    )
    if "IMPORTANT DISCLAIMER" not in content:
        return content + disclaimer
    return content

def extract_json(text: str) -> Dict[str, Any]:
    """Safely extracts JSON from model text."""
    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "content": text,
            "confidence": "Low",
            "follow_up_questions": [],
            "sources": []
        }
