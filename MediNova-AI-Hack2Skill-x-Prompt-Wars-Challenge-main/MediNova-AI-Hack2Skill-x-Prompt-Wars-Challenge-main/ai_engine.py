import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from utils import extract_json, append_disclaimer, logger
import prompt_templates as prompts
from search_engine import SearchEngine
from rag_engine import RAGEngine

class AIEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            logger.warning("GROQ_API_KEY is not set.")
            
        # Initialize GPT-OSS-20B via Groq compatible endpoint
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            api_key=api_key or "gsk_placeholder_key",
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
                "confidence": "Low",
                "follow_up_questions": [],
                "sources": []
            }
            
        return self._execute_prompt(prompts.CLINICSCOPE_PROMPT, {"url": url, "website_content": clean_text})