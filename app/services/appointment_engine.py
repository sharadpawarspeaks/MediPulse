import logging
from typing import Dict, Any, List, Optional
import datetime

logger = logging.getLogger("MediPulse.AppointmentEngine")

class AppointmentEngine:
    """
    Doctor Appointment Preparation Sheet Generator.
    Helps patients organize symptoms, timeline, current medications,
    and high-yield questions for their clinician into a clean, print-ready document.
    """

    @classmethod
    def generate_prep_sheet(
        cls,
        chief_complaint: str,
        symptom_timeline: Optional[str] = None,
        current_meds: Optional[str] = None,
        known_allergies: Optional[str] = None,
        key_questions: Optional[str] = None,
        doctor_specialty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes user-provided information into a structured appointment checklist.
        All information is explicitly labeled as patient-reported or AI-suggested.
        """
        today_str = datetime.date.today().strftime("%B %d, %Y")

        # Synthesize questions for doctor
        suggested_questions: List[str] = [
            "What do you believe is the most probable cause of these symptoms?",
            "Are there specific diagnostic tests or imaging you recommend to confirm?",
            "What warning signs or 'red flags' should prompt me to seek emergency care?",
            "Are there non-pharmacological lifestyle adjustments or self-care measures that can help?",
            "If prescribed medications, what are the anticipated benefits, common side effects, and timeframe for improvement?"
        ]

        if key_questions and key_questions.strip():
            user_q_list = [q.strip() for q in key_questions.split("\n") if q.strip()]
        else:
            user_q_list = []

        combined_questions = user_q_list + [q for q in suggested_questions if q not in user_q_list]

        # Markdown formatted report for preview and printing
        sheet_markdown = f"""# MediPulse Doctor Visit Preparation Summary
**Generated:** {today_str} | **Intended Specialty:** {doctor_specialty or 'General Consultation'}

---

### 1. Primary Reason for Visit (Chief Concern)
*Patient Reported:*
> {chief_complaint.strip()}

### 2. Symptom History & Timeline
*Patient Reported:*
{symptom_timeline.strip() if symptom_timeline and symptom_timeline.strip() else 'No specific timeline provided by patient.'}

### 3. Current Medications & Supplements
*Patient Reported:*
{current_meds.strip() if current_meds and current_meds.strip() else 'None reported or to be verified during consultation.'}

### 4. Known Allergies & Sensitivities
*Patient Reported:*
{known_allergies.strip() if known_allergies and known_allergies.strip() else 'No known drug or food allergies reported.'}

---

### 5. High-Yield Questions to Ask Your Clinician
*Prioritized Discussion Points:*
"""
        for i, q in enumerate(combined_questions[:6], 1):
            sheet_markdown += f"{i}. {q}\n"

        sheet_markdown += """
---
### 6. Emergency Warning Reminders
If at any point before your consultation you experience **sudden crushing chest pain, difficulty breathing, slurred speech or facial droop, or heavy uncontrolled bleeding**, do not wait for an appointment—call your local emergency medical service immediately (112, 911, or 999).

---
*Notice: This document is an informational preparation tool compiled from patient-entered notes. It is NOT a clinical diagnosis or treatment order.*
"""

        return {
            "title": f"Doctor Visit Prep - {chief_complaint[:30]}",
            "date": today_str,
            "markdown": sheet_markdown,
            "chief_complaint": chief_complaint,
            "timeline": symptom_timeline or "",
            "medications": current_meds or "",
            "allergies": known_allergies or "",
            "questions": combined_questions[:6]
        }
