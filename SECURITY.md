# Security & Responsible AI Policy

## Healthcare Information & Safety Disclaimer
MediPulse is an educational and health literacy tool. It is engineered to help individuals understand health concepts, verify medical claims, and prepare for doctor visits. **It is NOT a medical device, diagnostic system, or clinical decision support software.**

- In any acute medical emergency, users must contact their local emergency services (112 in India/EU, 911 in USA, 999 in UK) or proceed directly to an emergency department.
- Users must always consult a licensed healthcare professional for clinical decisions, diagnoses, or medication changes.

---

## Reporting Vulnerabilities
We take the security and privacy of healthcare applications seriously. If you discover a security vulnerability (such as an SSRF bypass, prompt injection flaw, or sensitive data exposure):

1. **Do NOT open a public GitHub issue.**
2. Send a detailed report to the repository maintainer: `pawarsharad1205@gmail.com`
3. Include:
   - Vulnerability description and potential impact
   - Minimal reproducible proof of concept
   - Proposed mitigation if known
4. We will acknowledge receipt within 48 hours and work with you on a coordinated fix.

---

## Security Architecture in MediPulse

1. **SSRF Defense (Server-Side Request Forgery):**
   - The ClinicScope RAG engine strictly validates URL schemes (`http`, `https`).
   - Hostnames are resolved to IP addresses via DNS and checked against RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`, `::1`), and cloud metadata IP (`169.254.169.254`).
   - Maximum response sizes (4MB) and connection timeouts (25s) prevent resource exhaustion.

2. **Privacy by Design:**
   - Patient context profiles are stored exclusively on the client side in browser `localStorage`.
   - Uploaded medical lab reports are processed in-memory and immediately destroyed after analysis.
   - MediPulse does not log patient health content or retain chat logs in persistent databases.

3. **Secret Hygiene:**
   - API keys and tokens are loaded strictly from environment variables (`.env`).
   - `.env` is explicitly ignored by `.gitignore`.
   - Security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection`) are applied to every HTTP response.
