from app.services.report_engine import ReportEngine
from app.services.appointment_engine import AppointmentEngine

def test_report_biomarker_extraction():
    """Verify standard diagnostic markers are correctly extracted from report text."""
    sample_text = """
    METROPOLIS DIAGNOSTIC SERVICES
    Patient: Fictional Test Subject | Age: 42
    Complete Blood Count:
    Hemoglobin: 11.2 g/dL
    Total Leukocyte Count (WBC): 7200 /mcL
    Platelet Count: 185000 /mcL
    Biochemical Panel:
    Fasting Blood Sugar: 145 mg/dL
    HbA1c: 7.2%
    Serum Creatinine: 1.0 mg/dL
    Total Cholesterol: 218 mg/dL
    """
    analysis = ReportEngine.analyze_report_text(sample_text)
    assert len(analysis["detected_markers"]) >= 4
    names = [m["test_name"] for m in analysis["detected_markers"]]
    assert any("Hemoglobin" in n for n in names)
    assert any("Fasting" in n for n in names)
    assert any("HbA1c" in n for n in names)
    assert any("Platelet" in n for n in names)

def test_appointment_sheet_generation():
    """Verify AppointmentEngine generates structured doctor visit sheet."""
    prep = AppointmentEngine.generate_prep_sheet(
        chief_complaint="Persistent lower back stiffness after prolonged sitting",
        symptom_timeline="4 weeks",
        current_meds="Calcium, Vitamin D",
        known_allergies="No known drug allergies",
        key_questions="Should I get an MRI?\nCan I do yoga?",
        doctor_specialty="Spine Specialist"
    )
    assert "markdown" in prep
    assert "Chief Concern" in prep["markdown"]
    assert "Persistent lower back stiffness" in prep["markdown"]
    assert len(prep["questions"]) >= 2
