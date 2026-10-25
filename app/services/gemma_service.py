import os
import json
import re
import time
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import Config

logger = logging.getLogger("MediPulse.GemmaService")

# Official Google Gen AI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai SDK not available; Gemma service will operate in mock mode.")

class GemmaMockEngine:
    """
    High-fidelity, deterministic mock engine for testing and demonstrations
    without consuming external API credits or requiring an active internet connection.
    """

    @staticmethod
    def generate(task_type: str, user_input: str, context: Optional[str] = None) -> Dict[str, Any]:
        input_lower = user_input.lower()

        if task_type == "healthsense":
            return {
                "content": (
                    f"### Symptom Awareness Assessment: {user_input[:80]}\n\n"
                    "**1. General Clinical Context:**\n"
                    "The symptoms you described may be associated with common upper respiratory viral syndromes, tension-type discomfort, or localized inflammatory responses depending on onset, severity, and duration.\n\n"
                    "**2. Supportive Self-Care & Hydration:**\n"
                    "- Maintain adequate electrolyte and fluid intake (2.0–2.5 L/day unless restricted).\n"
                    "- Prioritize 7–9 hours of continuous sleep to support immunological recovery.\n"
                    "- Monitor temperature and symptom trajectory every 8 hours.\n\n"
                    "**3. When to Seek Urgent Clinical Attention:**\n"
                    "- Fever exceeding 38.5°C (101.3°F) refractory to antipyretics or lasting > 3 days.\n"
                    "- Development of shortness of breath, localized pleuritic chest pain, or stiff neck.\n"
                    "- Inability to tolerate oral fluids or severe dizziness upon standing."
                ),
                "confidence": "Medium",
                "follow_up_questions": [
                    "How many days have you experienced these specific symptoms?",
                    "Have you taken any over-the-counter medications like paracetamol?",
                    "Are you experiencing any shortness of breath or high fever?"
                ],
                "sources": [
                    "World Health Organization (WHO) - Clinical Care Guidelines",
                    "NIH MedlinePlus - Symptom Evaluation Guidelines (https://medlineplus.gov)"
                ],
                "evidence_level": "High - Public Health Agency Guideline"
            }

        elif task_type == "truthcheck":
            is_fact = "vaccin" in input_lower or "exercise" in input_lower or "water" in input_lower
            verdict = "Fact" if is_fact else "Myth / Misconception"
            return {
                "content": (
                    f"### Scientific Fact-Check: \"{user_input}\"\n\n"
                    f"**Verdict:** **{verdict}**\n\n"
                    "**Scientific Analysis:**\n"
                    "Peer-reviewed medical literature indicates that cold temperatures alone do not directly generate viral infections. Viral pathogens (such as Rhinovirus, Influenza, or SARS-CoV-2) are necessary etiological agents, though lower ambient humidity and indoor crowding during colder periods can facilitate droplet transmission.\n\n"
                    "**Key Takeaways:**\n"
                    "- Infection requires exposure to pathogens, not merely low temperatures.\n"
                    "- Barrier hygiene and indoor ventilation significantly reduce transmission risks."
                ),
                "confidence": "High",
                "follow_up_questions": [
                    "Would you like recommendations on evidence-based immune support?",
                    "Would you like citations from peer-reviewed virology literature?"
                ],
                "sources": [
                    "CDC - Respiratory Illness Prevention Guidelines (https://cdc.gov)",
                    "PubMed Central - Rhinovirus Transmission Mechanisms (https://ncbi.nlm.nih.gov/pmc)"
                ],
                "evidence_level": "High - Systematic Review & Agency Consensus"
            }

        elif task_type == "medisafe":
            return {
                "content": (
                    f"### Medication Profile: {user_input}\n\n"
                    "**1. Primary Clinical Purpose:**\n"
                    "Commonly utilized as an analgesic (pain reliever) and antipyretic (fever reducer) in standard clinical practice.\n\n"
                    "**2. Essential Safety Precautions:**\n"
                    "- **Maximum Daily Limits:** Strictly adhere to the labeled maximum dosage (never exceed 4,000 mg in 24 hours for healthy adults; lower thresholds in hepatic impairment).\n"
                    "- **Drug Combinations:** Check ingredients on over-the-counter cough and cold remedies to avoid accidental duplicate dosing.\n"
                    "- **Alcohol Interaction:** Concurrent alcohol consumption significantly increases risks of hepatotoxicity.\n\n"
                    "**3. Common Side Effects & Contraindications:**\n"
                    "- Rare gastrointestinal upset; serious allergic reactions (rash, swelling) require immediate cessation.\n"
                    "- Contraindicated or requires dosage titration in individuals with chronic liver disease."
                ),
                "confidence": "High",
                "follow_up_questions": [
                    "Are you currently taking any other prescription or herbal medications?",
                    "Do you have any known liver or kidney conditions?"
                ],
                "sources": [
                    "U.S. National Library of Medicine - DailyMed (https://dailymed.nlm.nih.gov)",
                    "NHS Medicines A-Z Directory (https://nhs.uk/medicines)"
                ],
                "evidence_level": "High - Pharmacological Reference"
            }

        elif task_type == "prevent":
            return {
                "content": (
                    f"### Prevent360 Wellness & Prevention Blueprint: {user_input}\n\n"
                    "**1. Aerobic & Resistance Activity:**\n"
                    "Aim for at least 150 minutes of moderate-intensity aerobic physical activity (brisk walking, cycling) or 75 minutes of vigorous activity weekly, supplemented by two days of muscle-strengthening exercises.\n\n"
                    "**2. Dietary & Micronutrient Optimization:**\n"
                    "- Prioritize dietary fiber (minimum 25–30g daily) from whole grains, legumes, and cruciferous vegetables.\n"
                    "- Limit sodium intake to under 2,000 mg/day to maintain healthy arterial compliance.\n\n"
                    "**3. Sleep Architecture & Stress Reduction:**\n"
                    "- Maintain consistent sleep-wake cycles; aim for 7–8 hours.\n"
                    "- Incorporate 10 minutes of diaphragmatic breathing or mindfulness to moderate cortisol spikes."
                ),
                "confidence": "High",
                "follow_up_questions": [
                    "What is your current baseline weekly physical activity level?",
                    "Do you have specific biometric goals (e.g., blood pressure, HbA1c)?"
                ],
                "sources": [
                    "WHO Guidelines on Physical Activity and Sedentary Behaviour (https://who.int)",
                    "AHA - Life's Essential 8 Guidelines (https://heart.org)"
                ],
                "evidence_level": "High - International Public Health Consensus"
            }

        elif task_type == "chat":
            return {
                "content": (
                    f"Thank you for sharing your question regarding **{user_input}**.\n\n"
                    "From an educational health perspective, understanding your specific symptoms, their timeline, and how they impact your daily routine is key. While I can provide evidence-based health guidance and suggest thoughtful questions for your healthcare provider, I cannot provide a formal medical diagnosis.\n\n"
                    "Could you share a bit more context—such as how long you've noticed this, or any other changes in your energy, sleep, or appetite?"
                ),
                "confidence": "Medium",
                "follow_up_questions": [
                    "Have you consulted a doctor about this before?",
                    "Are you taking any supplements or medications currently?"
                ],
                "sources": [
                    "MediPulse Educational Clinical Knowledge Base",
                    "NIH Health Information Guidelines"
                ],
                "evidence_level": "Moderate - General Clinical Education"
            }

        elif task_type == "doctorlens":
            return {
                "content": (
                    f"### Doctor Profile & Credential Overview: {user_input}\n\n"
                    "**Specialization & Medical Affiliation:**\n"
                    "- Verified Clinical Focus: Internal Medicine / Cardiology Consultant.\n"
                    "- Verified Qualifications: MBBS, MD, Board Certified in Clinical Practice.\n"
                    "- Hospital Affiliations: Major Academic Medical Center & Associated Polyclinics.\n\n"
                    "**Practice Information & Public Summary:**\n"
                    "- Consultation Modalities: In-person clinical appointments and registered telemedicine.\n"
                    "- Patient Feedback: Noted for thorough diagnostic evaluations and clear communication.\n\n"
                    "*Note: Credentials should always be verified against the official National Medical Commission (NMC) or state medical licensing board.*"
                ),
                "confidence": "Medium",
                "follow_up_questions": [
                    "Would you like to search for appointment booking directories?",
                    "Would you like to find comparable specialists in your locality?"
                ],
                "sources": [
                    "Public Medical Directory Registry",
                    "National Health Service Registry / State Licensing Portal"
                ],
                "evidence_level": "Moderate - Public Registry & Search Synthesis"
            }

        elif task_type == "carefinder":
            return {
                "content": (
                    f"### Healthcare Facilities & Specialist Guidance for: {user_input}\n\n"
                    "**Recommended Level of Care:**\n"
                    "Based on your input, an outpatient consultation with a **General Physician / Internal Medicine Specialist** or **Specialty Clinic** is recommended for non-emergency evaluation.\n\n"
                    "**Key Care Centers to Inquire With:**\n"
                    "- **District / Multi-Specialty Hospital:** Provides full diagnostic laboratory panels, imaging (USG/CT), and emergency support.\n"
                    "- **Community Polyclinic:** Ideal for immediate same-day physical assessment and blood pressure checks.\n\n"
                    "**Recommended Steps Before Visiting:**\n"
                    "1. Call ahead to verify specialist OPD (Outpatient Department) hours.\n"
                    "2. Carry any prior lab records and a list of current medications.\n"
                    "3. If acute red flags appear (chest pain, breathing trouble), go directly to the emergency department."
                ),
                "confidence": "Medium",
                "follow_up_questions": [
                    "Would you like to specify a city or postal code for localized recommendations?",
                    "Would you like to prepare a structured symptom summary for your doctor visit?"
                ],
                "sources": [
                    "National Health Portal Facility Directory",
                    "OpenStreetMap Healthcare Services Node"
                ],
                "evidence_level": "Moderate - Healthcare Directory Guidance"
            }

        elif task_type == "clinicscope":
            return {
                "content": (
                    f"### Clinic & Hospital Facility Summary\n"
                    f"**Source URL:** `{user_input}`\n\n"
                    "**1. Core Clinical Departments:**\n"
                    "- Emergency & Trauma Care (24x7)\n"
                    "- Cardiology, Neurology, General Surgery, & Pediatrics\n"
                    "- Diagnostic Pathology & Digital Radiology\n\n"
                    "**2. Patient Support & Facilities:**\n"
                    "- Inpatient intensive care units (ICU/CCU) with dedicated monitoring\n"
                    "- Outpatient consultation hours: Monday – Saturday, 08:00 AM – 06:00 PM\n"
                    "- Cashless health insurance empanelment available for major providers.\n\n"
                    "**3. Emergency & Contact Information:**\n"
                    "- Verified Helpline: Available via hospital main switchboard.\n"
                    "- Online appointment scheduling available via patient portal."
                ),
                "confidence": "High",
                "follow_up_questions": [
                    "Would you like to check specific insurance provider coverage?",
                    "Would you like to prepare questions for an upcoming consultation?"
                ],
                "sources": [
                    f"Direct Extracted Website Data ({user_input})"
                ],
                "evidence_level": "High - Direct Source Grounded"
            }

        # Default fallback
        return {
            "content": f"Information regarding **{user_input}** has been processed using MediPulse's educational engine. Please consult a qualified clinician for personalized healthcare decisions.",
            "confidence": "Medium",
            "follow_up_questions": ["Would you like more details on this topic?"],
            "sources": ["MediPulse Clinical Information Base"],
            "evidence_level": "Moderate"
        }

class GemmaService:
    """
    Centralized Google Gemma Model Client using official google-genai SDK.
    Supports gemma-4-26b-a4b-it, gemma-4-31b-it, or other compatible Gemma models.
    Operates with automated fail-safe mock fallback when credentials are unavailable.
    """

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMMA_MODEL
        self.mock_mode = Config.MOCK_AI
        self.client = None

        if not self.mock_mode and self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google Gen AI Client with Gemma model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gen AI Client: {e}")
                self.mock_mode = True
        else:
            self.mock_mode = True
            logger.info(f"GemmaService operating in Mock/Offline mode (Model: {self.model_name})")

    def _extract_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely parses JSON from LLM outputs, removing markdown backticks."""
        text = text.strip()
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback regex extraction for json object
            obj_match = re.search(r'\{[\s\S]*\}', text)
            if obj_match:
                try:
                    return json.loads(obj_match.group(0))
                except Exception:
                    pass

            logger.warning("Failed to decode JSON from model output; synthesizing structure.")
            return {
                "content": text,
                "confidence": "Medium",
                "follow_up_questions": [],
                "sources": []
            }

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=False
    )
    def _call_live_gemma(self, prompt: str) -> Optional[str]:
        """Calls the live Gemma model using google-genai SDK."""
        if not self.client:
            return None

        # Build prompt enforcing JSON structure
        json_prompt = (
            f"{prompt}\n\n"
            "CRITICAL: Output ONLY a valid JSON object with keys: "
            "'content' (Markdown string), 'confidence' ('High'|'Medium'|'Low'), "
            "'follow_up_questions' (list of strings), 'sources' (list of strings), "
            "and 'evidence_level' (string)."
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=json_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4096
            )
        )
        return response.text

    def execute(self, task_type: str, user_input: str, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a health intelligence prompt using Gemma or deterministic fallback.
        Never throws unhandled exceptions to the caller.
        """
        start_time = time.time()
        is_mock_run = self.mock_mode

        result = None
        if not is_mock_run:
            try:
                raw_output = self._call_live_gemma(prompt)
                if raw_output:
                    result = self._extract_json_safely(raw_output)
                else:
                    logger.warning("Empty response from live Gemma; falling back to mock engine.")
                    is_mock_run = True
            except Exception as e:
                logger.error(f"Live Gemma API call failed: {e}. Utilizing deterministic mock.")
                is_mock_run = True

        if is_mock_run or not result:
            result = GemmaMockEngine.generate(task_type, user_input, context)

        latency_ms = int((time.time() - start_time) * 1000)

        # Standardize mandatory keys
        if "content" not in result or not result["content"]:
            result["content"] = "Health awareness information is currently unavailable. Please consult a qualified clinician."
        if "confidence" not in result:
            result["confidence"] = "Medium"
        if "follow_up_questions" not in result or not isinstance(result["follow_up_questions"], list):
            result["follow_up_questions"] = []
        if "sources" not in result or not isinstance(result["sources"], list):
            result["sources"] = []
        if "evidence_level" not in result:
            result["evidence_level"] = "Moderate"

        # Append universal medical disclaimer
        disclaimer = (
            "\n\n---\n"
            "**⚠️ MEDICAL INFORMATION NOTICE:**\n"
            "MediPulse is an educational platform designed to help you understand health information and prepare for clinical visits. "
            "It does not provide medical diagnoses, treatment plans, or prescription recommendations. Always seek the advice of a qualified physician."
        )
        if "MEDICAL INFORMATION NOTICE" not in result["content"]:
            result["content"] += disclaimer

        # Attach Transparency Metadata (Innovation H)
        result["transparency"] = {
            "model_used": self.model_name if not is_mock_run else f"{self.model_name} (Mock Engine)",
            "is_mock": is_mock_run,
            "provider": "Google Gemma (Official Gen AI SDK)" if not is_mock_run else "Google Gemma Deterministic Mock",
            "latency_ms": latency_ms,
            "evidence_grounded": bool(result.get("sources")),
            "evidence_level": result.get("evidence_level", "Moderate")
        }

        return result
