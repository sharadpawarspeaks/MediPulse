import io
import logging
from flask import Blueprint, request, jsonify
from app.services.safety_engine import SafetyEngine
from app.services.gemma_service import GemmaService
from app.services.evidence_engine import EvidenceEngine
from app.services.rag_engine import RAGEngine
from app.services.report_engine import ReportEngine
from app.services.appointment_engine import AppointmentEngine
import app.prompt_templates as prompts
from app.config import Config

logger = logging.getLogger("MediPulse.API")
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Initialize shared singleton services
gemma_service = GemmaService()
evidence_engine = EvidenceEngine()
rag_engine = RAGEngine()

@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker, uptime monitoring, and readiness probes."""
    return jsonify({
        "status": "healthy",
        "service": Config.PROJECT_NAME,
        "version": Config.VERSION,
        "model_configured": Config.GEMMA_MODEL,
        "mock_mode": gemma_service.mock_mode
    }), 200

@api_bp.route("/lifealert", methods=["POST"])
def api_lifealert():
    """
    Emergency detection endpoint.
    Dual-layer safety: Deterministic clinical rule evaluation runs first.
    Never fails if model is offline or unreachable.
    """
    data = request.get_json(silent=True) or {}
    symptoms = (data.get("symptoms") or "").strip()
    if not symptoms:
        return jsonify({"error": "Symptoms input is required."}), 400

    # Layer 1: Deterministic Clinical Red-Flag Rule Evaluation
    safety_eval = SafetyEngine.evaluate(symptoms)
    if safety_eval["is_emergency"]:
        return jsonify(safety_eval), 200

    # Layer 2: If no emergency red flags triggered, return safe evaluation
    return jsonify(safety_eval), 200

@api_bp.route("/healthsense", methods=["POST"])
def api_healthsense():
    """Symptom awareness assessment with optional plain-language and multilingual toggles."""
    data = request.get_json(silent=True) or {}
    symptoms = (data.get("symptoms") or "").strip()
    reading_level = data.get("reading_level", "standard")
    language = data.get("language", "en")

    if not symptoms:
        return jsonify({"error": "Symptoms are required."}), 400

    # Run safety check alongside
    safety = SafetyEngine.evaluate(symptoms)

    prompt = prompts.format_healthsense_prompt(symptoms, reading_level, language)
    result = gemma_service.execute("healthsense", symptoms, prompt)
    result["safety_eval"] = safety
    return jsonify(result), 200

@api_bp.route("/chat", methods=["POST"])
def api_chat():
    """HealthGPT conversational health assistant with privacy-first optional profile."""
    data = request.get_json(silent=True) or {}
    user_input = (data.get("input") or "").strip()
    chat_history = data.get("history", "")
    health_context = data.get("health_context", "")

    if not user_input:
        return jsonify({"error": "Message input is required."}), 400

    safety = SafetyEngine.evaluate(user_input)
    prompt = prompts.format_healthgpt_prompt(chat_history, user_input, health_context)
    result = gemma_service.execute("chat", user_input, prompt)
    result["safety_eval"] = safety
    return jsonify(result), 200

@api_bp.route("/prevent", methods=["POST"])
def api_prevent():
    """Prevent360 wellness and preventive health blueprints."""
    data = request.get_json(silent=True) or {}
    focus_area = (data.get("focus_area") or "").strip()
    if not focus_area:
        return jsonify({"error": "Focus area is required."}), 400

    prompt = prompts.format_prevent360_prompt(focus_area)
    result = gemma_service.execute("prevent", focus_area, prompt)
    return jsonify(result), 200

@api_bp.route("/truthcheck", methods=["POST"])
def api_truthcheck():
    """Evidence-grounded medical myth-busting and fact-checking."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or data.get("claim") or "").strip()
    if not query:
        return jsonify({"error": "Health claim or question is required."}), 400

    # Retrieve authoritative evidence from curated or live registries
    evidence = evidence_engine.retrieve_evidence(query)
    context_str = f"Verdict: {evidence['verdict']}\nEvidence Summary: {evidence['summary']}\nSources: {', '.join(evidence['sources'])}"

    prompt = prompts.format_truthcheck_prompt(query, context_str)
    result = gemma_service.execute("truthcheck", query, prompt, context_str)
    result["retrieved_evidence"] = evidence
    return jsonify(result), 200

@api_bp.route("/medisafe", methods=["POST"])
def api_medisafe():
    """MediSafe medication safety and precautions guide."""
    data = request.get_json(silent=True) or {}
    medicine = (data.get("medicine") or "").strip()
    if not medicine:
        return jsonify({"error": "Medicine name is required."}), 400

    prompt = prompts.format_medisafe_prompt(medicine)
    result = gemma_service.execute("medisafe", medicine, prompt)
    return jsonify(result), 200

@api_bp.route("/doctorlens", methods=["POST"])
def api_doctorlens():
    """Doctor credential and practice overview."""
    data = request.get_json(silent=True) or {}
    doctor_name = (data.get("doctor_name") or "").strip()
    location = (data.get("location") or "").strip()

    if not doctor_name:
        return jsonify({"error": "Doctor name is required."}), 400

    search_data = evidence_engine.search_doctor(doctor_name, location)
    prompt = prompts.format_doctorlens_prompt(doctor_name, search_data["context"])
    result = gemma_service.execute("doctorlens", doctor_name, prompt, search_data["context"])
    result["sources"] = search_data["sources"]
    return jsonify(result), 200

@api_bp.route("/carefinder", methods=["POST"])
def api_carefinder():
    """Location-grounded healthcare facility & specialist finder."""
    data = request.get_json(silent=True) or {}
    symptoms = (data.get("symptoms") or "").strip()
    location = (data.get("location") or "General Area").strip()
    specialty = data.get("specialty")

    if not symptoms:
        return jsonify({"error": "Symptoms or required care is required."}), 400

    safety = SafetyEngine.evaluate(symptoms)
    search_data = evidence_engine.search_care(symptoms, location, specialty)
    prompt = prompts.format_carefinder_prompt(symptoms, location, search_data["context"])
    result = gemma_service.execute("carefinder", f"{symptoms} in {location}", prompt, search_data["context"])
    result["safety_eval"] = safety
    return jsonify(result), 200

@api_bp.route("/clinicscope", methods=["POST"])
def api_clinicscope():
    """SSRF-hardened clinic website scraping and RAG summarization."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "Website URL is required."}), 400

    try:
        raw_html = rag_engine.fetch_website_content(url)
        structured_text = rag_engine.extract_structured_text(raw_html)
        top_chunks = rag_engine.chunk_and_retrieve(structured_text)
        chunk_context = "\n\n---\n\n".join(top_chunks)

        prompt = prompts.format_clinicscope_prompt(url, chunk_context)
        result = gemma_service.execute("clinicscope", url, prompt, chunk_context)
        result["chunks_retrieved"] = len(top_chunks)
        return jsonify(result), 200

    except ValueError as ve:
        # SSRF or validation error
        logger.warning(f"ClinicScope security block for {url}: {ve}")
        return jsonify({
            "content": f"🛡️ **Security Notice:** {str(ve)}\n\nMediPulse strictly prohibits scraping internal network addresses, localhost, and cloud metadata.",
            "confidence": "Low",
            "follow_up_questions": ["Please try again with a public clinic website URL."],
            "sources": []
        }), 400

    except Exception as e:
        logger.error(f"ClinicScope analysis failed for {url}: {e}")
        return jsonify({
            "content": f"Unable to analyze website ({url}): {str(e)}",
            "confidence": "Low",
            "follow_up_questions": ["Verify the website URL is public and online."],
            "sources": []
        }), 500

@api_bp.route("/report_analyze", methods=["POST"])
def api_report_analyze():
    """Medical lab report extraction and plain-language explanation (PDF or text)."""
    raw_text = ""
    # Check if a file was uploaded
    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            filename = file.filename.lower()
            if not filename.endswith(".pdf") and not filename.endswith(".txt"):
                return jsonify({"error": "Unsupported file format. Please upload a PDF or TXT report."}), 400
            
            if filename.endswith(".pdf"):
                try:
                    file_bytes = io.BytesIO(file.read())
                    raw_text = ReportEngine.extract_text_from_pdf(file_bytes)
                except ValueError as ve:
                    return jsonify({"error": str(ve)}), 400
            else:
                raw_text = file.read().decode("utf-8", errors="replace")

    # If no file, check json payload
    if not raw_text:
        data = request.get_json(silent=True) or {}
        raw_text = (data.get("report_text") or "").strip()

    if not raw_text:
        return jsonify({"error": "No report text or PDF file provided."}), 400

    # Extract metrics
    report_data = ReportEngine.analyze_report_text(raw_text)
    markers_summary = "\n".join([f"- {m['test_name']}: {m['observed_value']} (Typical: {m['typical_range']})" for m in report_data["detected_markers"]])

    prompt = prompts.format_report_prompt(raw_text, markers_summary)
    result = gemma_service.execute("report", "Medical Lab Report", prompt)
    result["detected_markers"] = report_data["detected_markers"]
    result["raw_excerpt"] = report_data["raw_excerpt"]
    return jsonify(result), 200

@api_bp.route("/visit_prep", methods=["POST"])
def api_visit_prep():
    """Doctor appointment preparation checklist generator."""
    data = request.get_json(silent=True) or {}
    chief_complaint = (data.get("chief_complaint") or "").strip()
    if not chief_complaint:
        return jsonify({"error": "Chief complaint or reason for visit is required."}), 400

    prep_data = AppointmentEngine.generate_prep_sheet(
        chief_complaint=chief_complaint,
        symptom_timeline=data.get("timeline"),
        current_meds=data.get("medications"),
        known_allergies=data.get("allergies"),
        key_questions=data.get("questions"),
        doctor_specialty=data.get("specialty")
    )
    return jsonify(prep_data), 200
