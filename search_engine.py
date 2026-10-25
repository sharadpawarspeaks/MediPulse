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
