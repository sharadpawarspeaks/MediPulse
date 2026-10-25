import pytest
from app import create_app
from app.config import Config

class TestConfig(Config):
    TESTING = True
    MOCK_AI = True
    SECRET_KEY = "test-secret-key"

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_pages_render_successfully(client):
    """Verify all web pages render with 200 status."""
    routes = ["/", "/doctor", "/clinic", "/report", "/visit-prep", "/offline"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Failed for route {route}"
        assert b"MediPulse" in response.data

def test_pwa_manifest_and_sw(client):
    """Verify Android PWA manifest and service worker are served properly."""
    res_manifest = client.get("/manifest.json")
    assert res_manifest.status_code == 200
    assert "application/manifest+json" in res_manifest.content_type
    assert b"MediPulse" in res_manifest.data

    res_sw = client.get("/sw.js")
    assert res_sw.status_code == 200
    assert "javascript" in res_sw.content_type
    assert res_sw.headers.get("Service-Worker-Allowed") == "/"

def test_health_check_endpoint(client):
    """Verify /api/health endpoint returns healthy status and metadata."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "MediPulse"
    assert "version" in data

def test_missing_fields_validation(client):
    """Verify all endpoints return 400 when required fields are missing."""
    endpoints = [
        ("/api/lifealert", {}),
        ("/api/healthsense", {}),
        ("/api/chat", {}),
        ("/api/prevent", {}),
        ("/api/truthcheck", {}),
        ("/api/medisafe", {}),
        ("/api/doctorlens", {}),
        ("/api/carefinder", {}),
        ("/api/clinicscope", {}),
        ("/api/report_analyze", {}),
        ("/api/visit_prep", {})
    ]
    for url, payload in endpoints:
        res = client.post(url, json=payload)
        assert res.status_code == 400, f"Expected 400 for {url} with empty payload"
        data = res.get_json()
        assert "error" in data

def test_healthsense_endpoint_success(client):
    """Verify HealthSense API returns structured guidance."""
    payload = {
        "symptoms": "Mild headache and low fatigue after screen work",
        "reading_level": "simple",
        "language": "en"
    }
    res = client.post("/api/healthsense", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "content" in data
    assert "confidence" in data
    assert "transparency" in data
    assert "IMPORTANT DISCLAIMER" in data["content"] or "MEDICAL INFORMATION NOTICE" in data["content"]

def test_truthcheck_endpoint_success(client):
    """Verify TruthCheck fact checks queries and provides sources."""
    payload = {"query": "Does cold weather cause fever?"}
    res = client.post("/api/truthcheck", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "content" in data
    assert "retrieved_evidence" in data
    assert len(data.get("sources", [])) > 0

def test_medisafe_endpoint_success(client):
    """Verify MediSafe returns safety precautions without prescribing."""
    payload = {"medicine": "Paracetamol"}
    res = client.post("/api/medisafe", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "content" in data
    assert "follow_up_questions" in data

def test_carefinder_endpoint_success(client):
    """Verify CareFinder accepts explicit location."""
    payload = {
        "symptoms": "Sprained ankle swelling",
        "location": "Mumbai Bandra",
        "specialty": "Orthopedics"
    }
    res = client.post("/api/carefinder", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "content" in data

def test_visit_prep_endpoint_success(client):
    """Verify CarePrep visit preparation generates checklist."""
    payload = {
        "chief_complaint": "Persistent knee discomfort after stairs",
        "timeline": "3 weeks",
        "specialty": "Orthopedic",
        "medications": "Vitamin D",
        "questions": "Do I need an X-ray?"
    }
    res = client.post("/api/visit_prep", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "markdown" in data
    assert "chief_complaint" in data
    assert len(data["questions"]) >= 1
