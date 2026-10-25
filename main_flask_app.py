"""
MediPulse Backward-Compatibility Entrypoint.
Preserves the original MediNova main_flask_app.py interface while delegating
to the modularized, security-hardened MediPulse application architecture.
"""
import os
from app import create_app
from app.services.gemma_service import GemmaService

app = create_app()
ai_engine = GemmaService()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true")
    app.run(host="0.0.0.0", port=port, debug=debug)
