import pytest
from app.services.rag_engine import RAGEngine

@pytest.fixture
def rag():
    return RAGEngine()

def test_ssrf_blocks_localhost(rag):
    """Verify localhost hostnames are strictly blocked."""
    prohibited_urls = [
        "http://localhost",
        "http://localhost:5000/admin",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "https://0.0.0.0",
        "http://[::1]"
    ]
    for url in prohibited_urls:
        with pytest.raises(ValueError) as excinfo:
            rag.validate_url(url)
        assert "prohibited" in str(excinfo.value).lower() or "blocked" in str(excinfo.value).lower()

def test_ssrf_blocks_cloud_metadata(rag):
    """Verify cloud metadata endpoint (169.254.169.254) is blocked."""
    with pytest.raises(ValueError):
        rag.validate_url("http://169.254.169.254/latest/meta-data/")

def test_ssrf_blocks_private_subnets(rag):
    """Verify RFC 1918 private subnets (10.x, 192.168.x, 172.16.x) are blocked."""
    private_urls = [
        "http://10.0.0.1/internal-status",
        "http://192.168.1.1/router",
        "http://172.16.0.5/api"
    ]
    for url in private_urls:
        with pytest.raises(ValueError):
            rag.validate_url(url)

def test_prohibited_scheme(rag):
    """Verify non-HTTP/HTTPS schemes (ftp, file, gopher) are rejected."""
    with pytest.raises(ValueError):
        rag.validate_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        rag.validate_url("ftp://example.com/data")

def test_rag_text_extraction_and_chunking(rag):
    """Verify HTML parsing strips scripts and retrieves relevant chunks."""
    sample_html = """
    <html>
        <head><title>Apex Multispecialty Hospital</title></head>
        <body>
            <script>alert('malicious')</script>
            <h1>Apex Multispecialty Hospital</h1>
            <p>Welcome to our regional medical facility providing world-class tertiary care.</p>
            <h2>Emergency & Trauma Department</h2>
            <p>Our 24-hour Emergency Department is equipped with level 1 trauma suites, cardiac resuscitation bays, and full diagnostic CT scanning.</p>
            <h2>Clinical Specialties</h2>
            <ul>
                <li>Cardiology & Cath Lab</li>
                <li>Neurology & Stroke Unit</li>
                <li>Orthopedic & Joint Replacement</li>
            </ul>
            <h2>Operating Hours & Cashless Insurance</h2>
            <p>OPD operates Monday through Saturday from 8 AM to 7 PM. Cashless empanelment is active for major TPA providers.</p>
        </body>
    </html>
    """
    clean_text = rag.extract_structured_text(sample_html)
    assert "alert('malicious')" not in clean_text
    assert "Apex Multispecialty Hospital" in clean_text
    assert "Emergency & Trauma Department" in clean_text

    # Test chunk retrieval
    chunks = rag.chunk_and_retrieve(clean_text, query="emergency trauma hours", top_k=2)
    assert len(chunks) > 0
    assert any("Emergency" in c or "Trauma" in c for c in chunks)
