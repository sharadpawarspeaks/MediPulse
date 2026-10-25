from app.services.gemma_service import GemmaService

def test_gemma_service_initialization():
    """Verify GemmaService initializes in test/mock mode without errors."""
    service = GemmaService()
    assert service is not None
    assert service.model_name is not None

def test_gemma_safe_json_parsing():
    """Verify safe JSON parsing parses clean, fenced, and recovers malformed JSON."""
    service = GemmaService()

    # Clean JSON
    res1 = service._extract_json_safely('{"content": "Hello", "confidence": "High"}')
    assert res1.get("content") == "Hello"
    assert res1.get("confidence") == "High"

    # Fenced JSON in markdown code blocks
    res2 = service._extract_json_safely("```json\n{\"content\": \"Fenced text\", \"confidence\": \"Medium\"}\n```")
    assert res2.get("content") == "Fenced text"

    # Malformed text
    res3 = service._extract_json_safely("Plain text without json structure")
    assert "content" in res3

def test_gemma_execution_attaches_transparency():
    """Verify execute() attaches required transparency metadata and disclaimer."""
    service = GemmaService()
    output = service.execute("healthsense", "sore throat", "Test prompt")
    assert "content" in output
    assert "transparency" in output
    assert "latency_ms" in output["transparency"]
    assert "model_used" in output["transparency"]
    assert "evidence_level" in output["transparency"]
    assert "MEDICAL INFORMATION NOTICE" in output["content"] or "IMPORTANT DISCLAIMER" in output["content"]
