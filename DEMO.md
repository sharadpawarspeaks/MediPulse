# MediPulse Hackathon Live Demonstration Guide

**Project Name:** MediPulse  
**Tagline:** Understand health information. Find evidence. Make informed next steps.  
**Primary AI Model:** Google Gemma (`gemma-4-26b-a4b-it`) via official `google-genai` SDK  
**Repository:** [https://github.com/sharadpawarspeaks/MediPulse](https://github.com/sharadpawarspeaks/MediPulse)  

---

## 3-Minute Live Presentation Script

### Minute 0:00 - 0:45 | The Problem & Value Proposition
> "Judges, every day hundreds of millions of people search the web for medical symptoms, receive incomprehensible lab reports, or encounter viral healthcare misinformation. The standard generative AI approach—attaching a generic chatbot to a text box—is dangerous: LLMs can hallucinate diagnoses, miss life-threatening cardiac symptoms, or invent fake citations.
>
> That is why we built **MediPulse**. MediPulse is an evidence-first, open-source healthcare intelligence platform powered by **Google Gemma**. It operates on three pillars: understand health information, find verifiable evidence, and make informed next steps."

### Minute 0:45 - 1:45 | Live Interactive Demonstration

#### 1. Instant 1-Click Guided Demo (For Judges)
> "Notice at the top of the MediPulse dashboard, we've embedded 4 one-click demo scenarios using fictional patient data so anyone can test the system without risking personal health information."

#### 2. Clinical Safety & LifeAlert Red-Flag Detection (Innovation Safety)
- Click **Scenario 1: Emergency Red-Flag** (`Sudden crushing chest pain radiating to left arm and jaw`).
- **What happens:** The deterministic safety rule engine immediately detects possible acute coronary syndrome, fires the top **Global Emergency Alert Banner** with 1-tap call to `112 / 911`, without waiting for an LLM network call!

#### 3. TruthCheck AI — Evidence-First Myth Busting (Innovation A)
- Click **Scenario 2: Medical Fact Check** (`Does cold winter air cause viral colds and fever?`).
- **What happens:** MediPulse queries authoritative medical consensus (WHO / CDC / NIH), classifies the verdict as a **Myth**, explains the rhinovirus pathogen mechanism, and displays transparent citations with an **Evidence Strength Level**!

#### 4. LabLens AI — Medical Report Translation (Innovation D)
- Click **Scenario 4: Lab Report Translation** (or paste `Hemoglobin: 11.2 g/dL, Fasting Blood Sugar: 145 mg/dL, HbA1c: 7.2%`).
- **What happens:** MediPulse extracts the biomarkers into a clean structured table with observed values and reference ranges, translates clinical jargon into plain English, and reminds the user that laboratory calibration varies.

#### 5. CarePrep AI — Doctor Visit Worksheet (Innovation F)
- Switch to **CarePrep AI**, enter a chief complaint, click **Generate Printable Visit Sheet**, then click **Print / Save as PDF**.
- **What happens:** A clean, print-ready clinician discussion guide is generated with a symptom timeline and prioritized discussion questions.

### Minute 1:45 - 2:30 | Technical Innovation Highlights

1. **Google Gemma Integration:** Powered by `gemma-4-26b-a4b-it` using the official `google-genai` Python SDK. Includes deterministic mock mode for keyless evaluations and automated testing.
2. **SSRF-Hardened Clinic RAG:** ClinicScope checks DNS hostnames and blocks localhost, RFC 1918 private subnets, and cloud metadata (`169.254.169.254`). Chunks web text and retrieves top sections using lexical scoring.
3. **Android Progressive Web App (PWA):** Features `manifest.json`, `sw.js` with offline fallback (`/offline`), fast installation prompt, and native mobile responsive UX.
4. **Privacy by Design:** Stored health context profiles exist solely in browser `localStorage`. No medical conversations are stored on remote databases.

### Minute 2:30 - 3:00 | Engineering Quality & Open-Source Readiness
> "MediPulse is production-grade open source: 25 automated unit tests passing in CI, Docker containerization, comprehensive security policies, and full MIT upstream attribution to MediNova by Shravan Shidruk. Thank you!"

---

## Step-by-Step Test Scenarios for Judges

| Tool | Input | Expected Behavior |
| :--- | :--- | :--- |
| **LifeAlert Safety** | `"Crushing chest pain and left arm numbness"` | Immediate red-flag trigger; emergency banner displayed; local hotlines provided. |
| **HealthSense** | `"Mild tension headache for 2 days"` | General physiological explanations; self-care hydration advice; warning signs. |
| **TruthCheck** | `"Do antibiotics cure the flu?"` | Verdict: Myth. Cites WHO Antimicrobial Resistance Guidelines. |
| **MediSafe** | `"Paracetamol"` | Explains analgesic purpose, 4000mg maximum limit, and alcohol contraindication. |
| **LabLens** | Upload PDF or paste lab text | Extracts markers (`Hb`, `FBS`, `HbA1c`), explains functions in plain English. |
| **CarePrep** | Knee pain complaint | Formats print-ready PDF appointment sheet. |
| **ClinicScope** | `https://www.aiims.edu` | Validates public URL, fetches content, chunks, and summarizes departments. |
| **SSRF Security** | `http://127.0.0.1:5000` | Blocked immediately with `400 Bad Request` security notice. |
