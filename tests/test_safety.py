from app.services.safety_engine import SafetyEngine

def test_cardiac_emergency_trigger():
    """Verify crushing chest pain radiating to left arm triggers CRITICAL emergency."""
    input_text = "I have severe crushing chest pain radiating to my left arm and jaw"
    result = SafetyEngine.evaluate(input_text)
    assert result["is_emergency"] is True
    assert result["severity"] == "CRITICAL"
    assert "heart attack" in result["warning_message"].lower() or "cardiac" in result["warning_message"].lower()
    assert "emergency_contacts" in result
    assert "112" in result["emergency_contacts"]["India"]
    assert "911" in result["emergency_contacts"]["USA"]

def test_fast_stroke_trigger():
    """Verify stroke FAST indicators trigger immediate emergency alert."""
    input_text = "My grandfather suddenly has facial droop and slurred speech"
    result = SafetyEngine.evaluate(input_text)
    assert result["is_emergency"] is True
    assert result["severity"] == "CRITICAL"
    assert "stroke" in result["warning_message"].lower()

def test_respiratory_cyanosis_trigger():
    """Verify acute dyspnea / blue lips trigger emergency."""
    input_text = "Patient cannot breathe, gasping for air with blue lips"
    result = SafetyEngine.evaluate(input_text)
    assert result["is_emergency"] is True
    assert result["severity"] == "CRITICAL"

def test_thunderclap_headache_trigger():
    """Verify sudden worst headache of life triggers HIGH severity warning."""
    input_text = "I have the sudden worst headache of my life with a stiff neck"
    result = SafetyEngine.evaluate(input_text)
    assert result["is_emergency"] is True
    assert result["severity"] in ("HIGH", "CRITICAL")

def test_non_emergency_condition():
    """Verify routine, non-emergency symptoms return is_emergency False."""
    input_text = "Mild runny nose and dry throat after gardening"
    result = SafetyEngine.evaluate(input_text)
    assert result["is_emergency"] is False
    assert result["severity"] == "NORMAL"
    assert result["warning_message"] == ""

def test_empty_or_whitespace_input():
    """Verify empty inputs fail safely without throwing exceptions."""
    assert SafetyEngine.evaluate("")["is_emergency"] is False
    assert SafetyEngine.evaluate("    ")["is_emergency"] is False
    assert SafetyEngine.evaluate(None)["is_emergency"] is False
