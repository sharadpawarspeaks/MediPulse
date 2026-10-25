"""
MediPulse AI Engine Compatibility Wrapper.
Wraps app.services.gemma_service.GemmaService with original methods.
"""
from app.services.gemma_service import GemmaService
from app.services.safety_engine import SafetyEngine
from app.services.evidence_engine import EvidenceEngine
from app.services.rag_engine import RAGEngine
import app.prompt_templates as prompts

class AIEngine:
    def __init__(self):
        self.gemma = GemmaService()
        self.evidence = EvidenceEngine()
        self.rag = RAGEngine()

    def is_emergency(self, symptoms: str) -> dict:
        return SafetyEngine.evaluate(symptoms)

    def get_healthsense(self, symptoms: str) -> dict:
        prompt = prompts.format_healthsense_prompt(symptoms)
        return self.gemma.execute("healthsense", symptoms, prompt)

    def chat_healthgpt(self, chat_history: str, user_input: str) -> dict:
        prompt = prompts.format_healthgpt_prompt(chat_history, user_input)
        return self.gemma.execute("chat", user_input, prompt)

    def get_prevent360(self, focus_area: str) -> dict:
        prompt = prompts.format_prevent360_prompt(focus_area)
        return self.gemma.execute("prevent", focus_area, prompt)

    def get_truthcheck(self, query: str) -> dict:
        evidence = self.evidence.retrieve_evidence(query)
        context = f"Verdict: {evidence['verdict']}\nSummary: {evidence['summary']}"
        prompt = prompts.format_truthcheck_prompt(query, context)
        return self.gemma.execute("truthcheck", query, prompt, context)

    def get_medisafe(self, medicine: str) -> dict:
        prompt = prompts.format_medisafe_prompt(medicine)
        return self.gemma.execute("medisafe", medicine, prompt)

    def get_doctorlens(self, doctor_name: str) -> dict:
        search_data = self.evidence.search_doctor(doctor_name)
        prompt = prompts.format_doctorlens_prompt(doctor_name, search_data["context"])
        return self.gemma.execute("doctorlens", doctor_name, prompt, search_data["context"])

    def get_carefinder(self, symptoms: str) -> dict:
        search_data = self.evidence.search_care(symptoms, "General Area")
        prompt = prompts.format_carefinder_prompt(symptoms, "General Area", search_data["context"])
        return self.gemma.execute("carefinder", symptoms, prompt, search_data["context"])

    def get_clinicscope(self, url: str) -> dict:
        try:
            raw_html = self.rag.fetch_website_content(url)
            clean_text = self.rag.extract_structured_text(raw_html)
            chunks = self.rag.chunk_and_retrieve(clean_text)
            chunk_context = "\n\n".join(chunks)
            prompt = prompts.format_clinicscope_prompt(url, chunk_context)
            return self.gemma.execute("clinicscope", url, prompt, chunk_context)
        except Exception as e:
            return {
                "content": f"Unable to analyze website: {str(e)}",
                "confidence": "Low",
                "follow_up_questions": [],
                "sources": []
            }
