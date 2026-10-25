<<<<<<< HEAD
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from utils import logger, retry_on_exception

class SearchEngine:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
        if not self.api_key:
            logger.warning("TAVILY_API_KEY is not set. Search features will fail.")

    @retry_on_exception(retries=3, backoff=2)
    def _tavily_search(self, query: str, search_depth: str = "advanced", max_results: int = 5) -> dict:
        """Core function to execute Tavily search API requests."""
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": False,
            "include_raw_content": False,
            "max_results": max_results,
            "include_domains": [],
            "exclude_domains": []
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily API error for query '{query}': {e}")
            raise Exception("Failed to retrieve search data.")

    def _format_results(self, raw_data: dict) -> str:
        """Extracts and formats search results for LLM consumption."""
        if not raw_data or "results" not in raw_data:
            return "No relevant information found."
        
        formatted_context = ""
        for idx, result in enumerate(raw_data["results"], 1):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            content = result.get("content", "No Content")
            formatted_context += f"[{idx}] {title}\nURL: {url}\nSummary: {content}\n\n"
        return formatted_context

    def search_doctor_info(self, doctor_name: str) -> str:
        """Searches for a specific doctor's profile and reviews."""
        query = f"{doctor_name} doctor reviews, specialization, hospital affiliation, awards"
        raw_data = self._tavily_search(query, max_results=4)
        return self._format_results(raw_data)

    def search_medical_fact(self, question: str) -> str:
        """Searches scientific sources for medical fact-checking."""
        query = f"scientific evidence medical fact check: {question}"
        raw_data = self._tavily_search(query, max_results=3)
        return self._format_results(raw_data)

    def find_nearby_healthcare(self, symptoms: str) -> str:
        """Uses concurrent requests to find various healthcare centers based on symptoms."""
        queries = [
            f"best hospitals for {symptoms} near me",
            f"clinics and specialists for {symptoms} near me"
        ]
        
        combined_context = ""
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Execute both searches simultaneously
            results = list(executor.map(lambda q: self._tavily_search(q, max_results=3), queries))
            
        for i, raw_data in enumerate(results):
            combined_context += f"--- Search Focus: {queries[i]} ---\n"
            combined_context += self._format_results(raw_data)
            
        return combined_context
=======
"""Compatibility wrapper for SearchEngine using EvidenceEngine."""
from app.services.evidence_engine import EvidenceEngine

class SearchEngine(EvidenceEngine):
    def search_doctor_info(self, doctor_name: str) -> str:
        return self.search_doctor(doctor_name)["context"]

    def search_medical_fact(self, question: str) -> str:
        evidence = self.retrieve_evidence(question)
        return f"{evidence['verdict']}: {evidence['summary']}"

    def find_nearby_healthcare(self, symptoms: str) -> str:
        return self.search_care(symptoms, "General Locality")["context"]
>>>>>>> origin/devFinal
