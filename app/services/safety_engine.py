import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("MediPulse.SafetyEngine")

class SafetyEngine:
    """
    Deterministic Clinical Red-Flag Rule Engine.
    Executes in <1ms without depending on external LLM calls to guarantee
    fail-safe emergency detection and life-saving guidance.
    """

    RED_FLAG_PATTERNS = [
        {
            "id": "cardiac_chest_pain",
            "name": "Possible Acute Coronary Syndrome (Heart Attack)",
            "regex": re.compile(
                r"\b(chest\s+pain|crushing\s+(chest|substernal)\s+pain|pressure\s+in\s+chest|tightness\s+in\s+chest|radiating\s+to\s+(left\s+arm|jaw|neck|back)|cardiac\s+arrest|myocardial\s+infarction)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Symptoms suggest possible acute cardiac ischemia or heart attack.",
            "action": "Do not drive yourself. Call emergency services immediately (112 in India/Europe, 911 in USA, 999 in UK) or seek urgent emergency transport to the nearest cath-lab enabled hospital."
        },
        {
            "id": "stroke_fast",
            "name": "Acute Neurological Deficit (FAST Stroke Signs)",
            "regex": re.compile(
                r"\b(face\s+droop|facial\s+droop|slurred\s+speech|speech\s+difficulty|arm\s+weakness|hemiplegia|one\s+side\s+paralysis|sudden\s+numbness\s+of\s+face|sudden\s+loss\s+of\s+vision|FAST\s+stroke)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Signs indicate possible acute cerebral stroke (Brain Attack). Time is brain.",
            "action": "Seek immediate emergency medical care. Immediate thrombolysis or thrombectomy window is time-critical."
        },
        {
            "id": "respiratory_distress",
            "name": "Severe Acute Respiratory Distress",
            "regex": re.compile(
                r"\b(cannot\s+breathe|gasping\s+for\s+air|severe\s+shortness\s+of\s+breath|blue\s+lips|cyanosis|stridor|choking|suffocating|struggling\s+to\s+breathe)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Critical compromise of airway or oxygenation detected.",
            "action": "Call local emergency services immediately. Sit upright, keep airway clear, and do not remain alone."
        },
        {
            "id": "anaphylaxis",
            "name": "Severe Allergic Anaphylaxis",
            "regex": re.compile(
                r"\b(throat\s+swelling|tongue\s+swelling|lips\s+swollen.*breathing|anaphylaxis|wheezing.*bee\s+sting|allergic\s+reaction.*cannot\s+breathe)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Features of systemic anaphylactic shock identified.",
            "action": "If prescribed, administer auto-injector Epinephrine (EpiPen) into outer mid-thigh immediately and call emergency services."
        },
        {
            "id": "severe_hemorrhage",
            "name": "Uncontrolled Massive Bleeding",
            "regex": re.compile(
                r"\b(pulsatile\s+bleeding|arterial\s+bleeding|spurting\s+blood|coughing\s+up\s+large\s+amounts\s+of\s+blood|massive\s+hemoptysis|vomiting\s+blood\s+profusely|hematemesis.*faint)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Potentially life-threatening acute hemorrhage.",
            "action": "Apply direct firm pressure with sterile gauze/clean cloth. Call emergency services without delay."
        },
        {
            "id": "altered_consciousness",
            "name": "Loss of Consciousness or Status Epilepticus",
            "regex": re.compile(
                r"\b(unresponsive|loss\s+of\s+consciousness|blacked\s+out.*head\s+injury|continuous\s+seizure|seizure\s+longer\s+than\s+5\s+minutes|coma|cannot\s+be\s+woken)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Severe neurological emergency or prolonged seizure activity.",
            "action": "Place patient in lateral recovery position if safe. Ensure clear airway. Call emergency dispatch immediately."
        },
        {
            "id": "thunderclap_headache",
            "name": "Sudden Worst Headache of Life",
            "regex": re.compile(
                r"\b(thunderclap\s+headache|worst\s+headache\s+of\s+my\s+life|sudden\s+explosive\s+headache|headache\s+with\s+stiff\s+neck\s+and\s+fever)\b",
                re.IGNORECASE
            ),
            "severity": "HIGH",
            "warning": "Warning sign for intracranial hemorrhage or acute meningeal infection.",
            "action": "Go immediately to the nearest hospital Emergency Room for urgent neuroimaging evaluation."
        },
        {
            "id": "suicide_crisis",
            "name": "Psychiatric Emergency / Self-Harm Crisis",
            "regex": re.compile(
                r"\b(suicide|kill\s+myself|end\s+my\s+life|want\s+to\s+die|harm\s+myself|take\s+all\s+my\s+pills)\b",
                re.IGNORECASE
            ),
            "severity": "CRITICAL",
            "warning": "Immediate mental health crisis support is available 24/7.",
            "action": "Please reach out immediately. In India: Tele-MANAS at 14416 / 1800-891-4416 or KIRAN at 1800-599-0019. In the USA/Canada: Call or text 988. In the UK: Call 111 or Samaritans at 116 123. In Europe/International: Call 112 or contact your local crisis lifeline."
        }
    ]

    @classmethod
    def evaluate(cls, text: str) -> Dict[str, Any]:
        """
        Evaluates input text against clinically validated emergency red flags.
        Always succeeds deterministically even without an internet connection or LLM.
        """
        if not text or not isinstance(text, str):
            return {
                "is_emergency": False,
                "severity": "NONE",
                "matched_red_flags": [],
                "warning_message": "",
                "recommendation": ""
            }

        matched_flags: List[Dict[str, str]] = []
        highest_severity = "NONE"

        for rule in cls.RED_FLAG_PATTERNS:
            if rule["regex"].search(text):
                matched_flags.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "warning": rule["warning"],
                    "action": rule["action"]
                })
                if rule["severity"] == "CRITICAL":
                    highest_severity = "CRITICAL"
                elif rule["severity"] == "HIGH" and highest_severity != "CRITICAL":
                    highest_severity = "HIGH"

        if matched_flags:
            primary = matched_flags[0]
            return {
                "is_emergency": True,
                "severity": highest_severity,
                "matched_red_flags": [f["name"] for f in matched_flags],
                "warning_message": f"🚨 EMERGENCY RED FLAG DETECTED: {primary['warning']}",
                "recommendation": primary["action"],
                "emergency_contacts": {
                    "India": "112 (National Emergency), 108 (Ambulance), 14416 (Tele-MANAS Mental Health)",
                    "USA": "911 (Emergency), 988 (Suicide & Crisis Lifeline)",
                    "UK": "999 (Emergency), 111 (NHS Urgent Care)",
                    "Europe": "112 (Universal Emergency Number)",
                    "General": "Contact your local emergency medical service or proceed to the nearest Emergency Department immediately."
                }
            }

        return {
            "is_emergency": False,
            "severity": "NORMAL",
            "matched_red_flags": [],
            "warning_message": "",
            "recommendation": "No acute emergency red flags detected based on rule patterns. Continue to monitor symptoms and consult a licensed clinician for persistent, worsening, or concerning health issues."
        }
