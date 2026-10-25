<<<<<<< HEAD
import os
import json
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils import extract_json, append_disclaimer, logger
import prompt_templates as prompts
from search_engine import SearchEngine
from rag_engine import RAGEngine

class AIEngine:
    def __init__(self):
        gemma_key = os.getenv("GEMMA_API_KEY") or os.getenv("APIM_API_KEY")
        gemma_endpoint = os.getenv("GEMMA_ENDPOINT") or os.getenv("APIM_ENDPOINT")
        model_name = os.getenv("GEMMA_MODEL_NAME", "gemma-4-26b-a4b-it")
        groq_key = os.getenv("GROQ_API_KEY")

        # Prioritize Gemma 4 26B A4B IT
        if gemma_key or gemma_endpoint or not groq_key:
            if not gemma_key:
                logger.warning("GEMMA_API_KEY is not set in .env.")
            else:
                logger.info(f"Initialized Gemma model: {model_name}")

            headers = {}
            if gemma_key:
                headers["api-key"] = gemma_key
                headers["Ocp-Apim-Subscription-Key"] = gemma_key

            llm_kwargs = {
                "model": model_name,
                "api_key": gemma_key or "placeholder_key",
                "temperature": 0.3,
                "max_tokens": 4096
            }
            if gemma_endpoint:
                llm_kwargs["base_url"] = gemma_endpoint
            if headers:
                llm_kwargs["default_headers"] = headers

            self.llm = ChatOpenAI(**llm_kwargs)
        else:
            logger.info("Initializing fallback Groq model")
            self.llm = ChatGroq(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                api_key=groq_key or "gsk_placeholder_key",
                temperature=0.3,
                max_tokens=6000
            )
        
        self.search_engine = SearchEngine()
        self.rag_engine = RAGEngine()

    def _execute_prompt(self, prompt_template: PromptTemplate, kwargs: dict) -> dict:
        """Executes the chain and safely parses the JSON response."""
        try:
            chain = prompt_template | self.llm
            response = chain.invoke(kwargs)
            raw_text = response.content
            
            # Extract and validate JSON
            data = extract_json(raw_text)
            
            # Ensure mandatory keys exist
            for key in ["content", "confidence", "follow_up_questions", "sources"]:
                if key not in data:
                    data[key] = [] if key in ["follow_up_questions", "sources"] else "Data unavailable"
                    
            # Apply Disclaimer
            data["content"] = append_disclaimer(data["content"])
            return data
            
        except Exception as e:
            logger.error(f"Error executing AI prompt: {e}")
            return {
                "content": "I apologize, but I am currently unable to process your request due to a technical error. Please try again.",
                "confidence": "Low",
                "follow_up_questions": [],
                "sources": []
            }

    def is_emergency(self, symptoms: str) -> dict:
        """Fast parallel check for emergency situations."""
        try:
            chain = prompts.LIFEALERT_PROMPT | self.llm
            response = chain.invoke({"symptoms": symptoms})
            return extract_json(response.content)
        except Exception as e:
            logger.error(f"LifeAlert error: {e}")
            return {"is_emergency": False, "warning_message": "", "recommendation": ""}

    def get_healthsense(self, symptoms: str) -> dict:
        """Analyzes symptoms for health awareness."""
        return self._execute_prompt(prompts.HEALTHSENSE_PROMPT, {"symptoms": symptoms})

    def chat_healthgpt(self, chat_history: str, user_input: str) -> dict:
        """Conversational health assistant."""
        return self._execute_prompt(prompts.HEALTHGPT_PROMPT, {
            "chat_history": chat_history,
            "user_input": user_input
        })

    def get_prevent360(self, focus_area: str) -> dict:
        """Generates preventive care plans."""
        return self._execute_prompt(prompts.PREVENT360_PROMPT, {"focus_area": focus_area})

    def get_medisafe(self, medicine: str) -> dict:
        """Provides medicine safety information."""
        return self._execute_prompt(prompts.MEDISAFE_PROMPT, {"medicine": medicine})

    def get_truthcheck(self, query: str) -> dict:
        """Fact checks medical myths using Tavily."""
        try:
            context = self.search_engine.search_medical_fact(query)
        except Exception:
            context = "Unable to fetch live search data."
        return self._execute_prompt(prompts.TRUTHCHECK_PROMPT, {"query": query, "search_context": context})

    def get_doctorlens(self, doctor_name: str) -> dict:
        """Looks up doctor information."""
        try:
            context = self.search_engine.search_doctor_info(doctor_name)
        except Exception:
            context = "Unable to fetch live search data."
        return self._execute_prompt(prompts.DOCTORLENS_PROMPT, {"doctor_name": doctor_name, "search_context": context})

    def get_carefinder(self, symptoms: str) -> dict:
        """Finds nearby healthcare based on symptoms."""
        try:
            context = self.search_engine.find_nearby_healthcare(symptoms)
        except Exception:
            context = "Unable to fetch live search data."
        return self._execute_prompt(prompts.CAREFINDER_PROMPT, {"symptoms": symptoms, "search_context": context})

    def get_clinicscope(self, url: str) -> dict:
        """Scrapes and summarizes clinic websites."""
        try:
            raw_text = self.rag_engine.fetch_website_content(url)
            clean_text = self.rag_engine.chunk_content(raw_text)
        except Exception as e:
            return {
                "content": f"Failed to analyze website: {str(e)}",
=======
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
>>>>>>> origin/devFinal
                "confidence": "Low",
                "follow_up_questions": [],
                "sources": []
            }
<<<<<<< HEAD
            
        return self._execute_prompt(prompts.CLINICSCOPE_PROMPT, {"url": url, "website_content": clean_text})
=======
>>>>>>> origin/devFinal
