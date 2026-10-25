# Contributing to MediPulse

Thank you for your interest in contributing to **MediPulse**! We welcome contributions from developers, clinicians, UI/UX designers, accessibility advocates, and open-source enthusiasts.

---

## Code of Conduct & Healthcare Principles
MediPulse is committed to responsible, safe healthcare information engineering:
1. **Never Invent Medical Facts:** Citations, statistics, drug dosages, and clinical guidelines must always be grounded in recognized medical sources (WHO, CDC, NIH, NHS, PubMed).
2. **Clinical Safety First:** Emergency detection logic must never rely solely on probabilistic LLM responses; deterministic safety checks take precedence.
3. **Privacy by Design:** Personal health details must never be stored on remote servers or transmitted to unvetted third parties without explicit user consent.
4. **Respect & Inclusion:** Maintain an empathetic, constructive environment across all issues and pull requests.

---

## Development Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.13, and 3.14)
- Git

### 2. Fork and Clone
```bash
git clone https://github.com/<your-username>/MediPulse.git
cd MediPulse
```

### 3. Create a Virtual Environment
```bash
# On Linux/macOS
python -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY` (from [Google AI Studio](https://aistudio.google.com/)). If you don't have a key yet, leave it blank; MediPulse automatically runs in deterministic mock mode for local testing!

### 6. Run the Test Suite
```bash
pytest -v
```

### 7. Start Local Development Server
```bash
python app.py
```
Open your browser at `http://localhost:5000`.

---

## Contribution Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write clean, modular code with comments and unit tests in `tests/`.
3. Verify all tests pass:
   ```bash
   pytest -v
   ```
4. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "feat(report): add support for lipid panel ratio calculations"
   ```
5. Push to your fork and submit a Pull Request to `main`.

---

## Hacktoberfest & Issue Roadmap
We have tagged issues suitable for contributors:
- [ ] Add support for additional Indian regional languages (Marathi, Tamil, Telugu, Bengali).
- [ ] Implement DICOM header inspection for imaging reports.
- [ ] Expand deterministic emergency rules to cover pediatric respiratory signs (stridor, retractions).
- [ ] Add offline PWA background sync for appointment worksheet drafts.
- [ ] Integrate ICD-10 educational mapping for symptom awareness.
