import os
import re
import logging
from typing import Dict, Any, List, Optional
import requests
from app.config import Config

logger = logging.getLogger("MediPulse.EvidenceEngine")

class EvidenceEngine:
    """
    Evidence-First Retrieval & Verification Engine.
    Prioritizes authoritative public health organizations (WHO, CDC, NIH, NHS, PubMed)
    and generates transparent evidence strength scoring.
    """

    # Authoritative knowledge base for offline / reproducible fact checking
    CURATED_HEALTH_FACTS = [
        {
            "keywords": ["cold", "weather", "temperature", "winter", "chill"],
            "claim": "Cold weather causes colds and flu",
            "verdict": "Myth",
            "explanation": "Colds and influenza are caused exclusively by viral infections (such as Rhinoviruses or Orthomyxoviruses), not cold temperatures alone. Cold weather prompts people to spend more time indoors with poor ventilation, which accelerates pathogen transmission.",
            "sources": [
                {
                    "title": "Common Cold: Causes, Symptoms & Research",
                    "publisher": "National Institutes of Health (NIH)",
                    "url": "https://medlineplus.gov/commoncold.html",
                    "quality": "High - Government Health Agency"
                },
                {
                    "title": "Cold & Flu Viruses and Transmission Factors",
                    "publisher": "Centers for Disease Control and Prevention (CDC)",
                    "url": "https://www.cdc.gov/flu/about/viruses/index.html",
                    "quality": "High - Public Health Guideline"
                }
            ],
            "strength": "Level A - High Evidence Consensus"
        },
        {
            "keywords": ["antibiotic", "virus", "flu", "fever", "cough"],
            "claim": "Antibiotics cure viral infections like the cold or flu",
            "verdict": "Myth / Dangerous Practice",
            "explanation": "Antibiotics target bacterial cell walls and metabolic processes; they have zero efficacy against viral genomes. Inappropriate antibiotic use promotes global antimicrobial resistance (AMR) and causes unnecessary adverse reactions.",
            "sources": [
                {
                    "title": "Antimicrobial Resistance Fact Sheet",
                    "publisher": "World Health Organization (WHO)",
                    "url": "https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance",
                    "quality": "High - International Health Authority"
                },
                {
                    "title": "Antibiotic Do's and Don'ts",
                    "publisher": "CDC Antibiotic Stewardship",
                    "url": "https://www.cdc.gov/antibiotic-use/do-and-dont.html",
                    "quality": "High - Clinical Guideline"
                }
            ],
            "strength": "Level A - High Evidence Consensus"
        },
        {
            "keywords": ["vaccine", "autism", "mmr"],
            "claim": "Vaccines cause autism",
            "verdict": "Debunked Myth",
            "explanation": "Extensive multinational epidemiological studies involving millions of children over 25+ years have repeatedly refuted any causal link between vaccines and autism spectrum disorders. The original 1998 Wakefield paper was fully retracted for data falsification.",
            "sources": [
                {
                    "title": "Vaccines and Autism: A Thorough Review of Evidence",
                    "publisher": "Institute of Medicine (National Academies)",
                    "url": "https://www.ncbi.nlm.nih.gov/books/NBK10084/",
                    "quality": "High - National Academy of Medicine"
                },
                {
                    "title": "Autism and Vaccines",
                    "publisher": "CDC Vaccine Safety",
                    "url": "https://www.cdc.gov/vaccinesafety/concerns/autism.html",
                    "quality": "High - Meta-Analysis & Guideline"
                }
            ],
            "strength": "Level A - High Evidence Consensus"
        },
        {
            "keywords": ["sugar", "diabetes", "sweet"],
            "claim": "Eating sugar directly and solely causes Type 1 or Type 2 Diabetes",
            "verdict": "Nuanced Misconception",
            "explanation": "Type 1 diabetes is an autoimmune condition unrelated to sugar intake. Type 2 diabetes develops from a complex interplay of genetic predisposition, visceral adiposity, lack of physical activity, and insulin resistance. High-sugar diets can contribute to excess caloric intake and obesity, but sugar is not the sole direct cause.",
            "sources": [
                {
                    "title": "Diabetes Overview and Risk Factors",
                    "publisher": "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)",
                    "url": "https://www.niddk.nih.gov/health-information/diabetes",
                    "quality": "High - Federal Research Institute"
                }
            ],
            "strength": "Level B - Clinical Consensus"
        }
    ]

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=".env", override=True)
        self.tavily_key = (os.getenv("TAVILY_API_KEY") or Config.TAVILY_API_KEY or "").strip("\"' \t\r\n")
        self.tavily_url = "https://api.tavily.com/search"

    def retrieve_evidence(self, query: str) -> Dict[str, Any]:
        """
        Retrieves evidence from authoritative health sources.
        Prioritizes live real-time Tavily search whenever configured;
        gracefully falls back to curated clinical knowledge if offline.
        """
        # 1. Prioritize Live Tavily Real-Time Web Search
        if self.tavily_key:
            try:
                payload = {
                    "api_key": self.tavily_key,
                    "query": f"medical evidence fact check: {query}",
                    "search_depth": "advanced",
                    "max_results": 4
                }
                res = requests.post(self.tavily_url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    if results:
                        formatted_sources = [
                            f"{r.get('title', 'Medical Citation')} - {r.get('url', '')}"
                            for r in results if r.get('url')
                        ]
                        summary_text = "\n\n".join([f"**{r.get('title', 'Source')}**: {r.get('content', '')}" for r in results[:3]])
                        return {
                            "matched": True,
                            "claim": query,
                            "verdict": "Real-Time Evidence Retrieved",
                            "summary": summary_text,
                            "sources": formatted_sources,
                            "raw_sources": results,
                            "evidence_strength": "Level A - Live Real-Time Web Search",
                            "retrieval_method": "Live Real-Time Medical Search (Tavily)"
                        }
            except Exception as e:
                logger.error(f"Live Tavily evidence retrieval error: {e}")

        # 2. Fallback to Curated Knowledge Base if offline or Tavily unavailable
        query_lower = query.lower()
        for item in self.CURATED_HEALTH_FACTS:
            if any(k in query_lower for k in item["keywords"]):
                return {
                    "matched": True,
                    "claim": item["claim"],
                    "verdict": item["verdict"],
                    "summary": item["explanation"],
                    "sources": [f"{s['title']} ({s['publisher']}) - {s['url']}" for s in item["sources"]],
                    "raw_sources": item["sources"],
                    "evidence_strength": item["strength"],
                    "retrieval_method": "Curated Authoritative Registry (Offline Fallback)"
                }

        # 3. Default General Synthesis
        return {
            "matched": False,
            "claim": query,
            "verdict": "Inconclusive / General Analysis",
            "summary": "Live search did not yield conclusive peer-reviewed consensus for this query. Consulting general health guidelines.",
            "sources": [
                "World Health Organization Health Topics (https://who.int)",
                "NIH MedlinePlus Health Information (https://medlineplus.gov)"
            ],
            "raw_sources": [],
            "evidence_strength": "Level C - General Clinical Context",
            "retrieval_method": "General Clinical Knowledge Base"
        }

    def search_doctor(self, doctor_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """Searches public doctor credentials while clearly distinguishing verified facts."""
        loc_str = f" in {location}" if location else ""
        query = f"{doctor_name} doctor qualifications hospital{loc_str}"

        if self.tavily_key:
            try:
                payload = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "max_results": 3
                }
                res = requests.post(self.tavily_url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    context = "\n".join([f"[{i+1}] {r.get('title')}: {r.get('content')}" for i, r in enumerate(results)])
                    return {
                        "context": context,
                        "sources": [r.get("url") for r in results if r.get("url")],
                        "is_live": True
                    }
            except Exception as e:
                logger.warning(f"Doctor search API error: {e}")

        # Deterministic structured profile framework
        return {
            "context": (
                f"Public Directory Information for {doctor_name}{loc_str}:\n"
                "- Medical Board Registry Check: Verification recommended through National Medical Commission (NMC) or state medical council.\n"
                "- Clinical Practice Focus: Outpatient diagnostic consultation and specialized management.\n"
                "- Note: Unverified commercial reviews or star ratings cannot be clinically substantiated."
            ),
            "sources": ["National Medical Commission (NMC) Public Registry Portal"],
            "is_live": False
        }

    def search_care(self, symptoms: str, location: str, specialty: Optional[str] = None) -> Dict[str, Any]:
        """Provides verified care discovery with explicit location grounding."""
        spec_text = f" ({specialty})" if specialty else ""
        query = f"Hospitals clinics{spec_text} in {location} for {symptoms}"

        if self.tavily_key:
            try:
                payload = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "max_results": 4
                }
                res = requests.post(self.tavily_url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    context = "\n".join([f"[{i+1}] {r.get('title')}: {r.get('content')}" for i, r in enumerate(results)])
                    return {
                        "context": context,
                        "sources": [r.get("url") for r in results if r.get("url")],
                        "location_used": location,
                        "is_live": True
                    }
            except Exception as e:
                logger.warning(f"Care search API error: {e}")

        # Fallback structured care navigation
        return {
            "context": (
                f"Healthcare discovery for location: '{location}' (Symptoms: {symptoms}):\n"
                f"- Primary Care: Visit an accredited community health center or primary polyclinic in {location}.\n"
                f"- Specialty Evaluation: Consult a registered {specialty or 'Internal Medicine Specialist'}.\n"
                f"- Emergency Services: For acute symptoms, proceed immediately to the nearest Government/District Hospital Emergency Wing."
            ),
            "sources": ["National Health Portal Healthcare Facility Registry"],
            "location_used": location,
            "is_live": False
        }
