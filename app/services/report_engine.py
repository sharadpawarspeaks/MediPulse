import re
import io
import logging
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

logger = logging.getLogger("MediPulse.ReportEngine")

class ReportEngine:
    """
    Medical Lab Report Understanding Engine.
    Faithfully extracts laboratory metrics, units, and reference ranges from
    PDF documents or raw text inputs, and translates clinical jargon into plain English.
    """

    KNOWN_LAB_MARKERS = [
        {
            "name": "Hemoglobin (Hb)",
            "regex": re.compile(r"\b(hemoglobin|hb)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "13.5–17.5 g/dL (Adult Male), 12.0–15.5 g/dL (Adult Female)",
            "plain_explanation": "Hemoglobin is an iron-rich protein in red blood cells that transports oxygen from your lungs to the rest of your body."
        },
        {
            "name": "Fasting Blood Glucose",
            "regex": re.compile(r"\b(fasting\s+(?:blood\s+)?(?:sugar|glucose)|fbs)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "70–99 mg/dL (Normal Fasting)",
            "plain_explanation": "Measures circulating blood sugar levels after an overnight fast (minimum 8 hours). Helps evaluate glucose metabolism."
        },
        {
            "name": "Glycated Hemoglobin (HbA1c)",
            "regex": re.compile(r"\b(hba1c|glycated\s+hemoglobin)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "Below 5.7% (Normal), 5.7%–6.4% (Prediabetes), >=6.5% (Diabetes)",
            "plain_explanation": "Reflects your average blood glucose levels over the preceding 2 to 3 months by measuring sugar attached to red blood cells."
        },
        {
            "name": "Platelet Count",
            "regex": re.compile(r"\b(platelets?|platelet\s+count)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "150,000–450,000 /mcL (or 1.5–4.5 Lakhs/mcL)",
            "plain_explanation": "Cell fragments essential for normal blood clotting and stopping bleeding when blood vessels are injured."
        },
        {
            "name": "Serum Creatinine",
            "regex": re.compile(r"\b(creatinine|serum\s+creatinine)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "0.7–1.3 mg/dL (Adult Male), 0.5–1.1 mg/dL (Adult Female)",
            "plain_explanation": "A breakdown byproduct of normal muscle metabolism filtered by the kidneys. Used as a key biomarker of renal filtration efficiency."
        },
        {
            "name": "Total Cholesterol",
            "regex": re.compile(r"\b(total\s+cholesterol)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "Desirable: Under 200 mg/dL",
            "plain_explanation": "The overall measure of blood lipids, combining low-density lipoprotein (LDL), high-density lipoprotein (HDL), and triglycerides."
        },
        {
            "name": "White Blood Cell (WBC) Count",
            "regex": re.compile(r"\b(wbc|total\s+leukocyte\s+count|tlc)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "4,000–11,000 cells/mcL",
            "plain_explanation": "The primary cells of the immune system that defend against bacterial, viral, and inflammatory challenges."
        },
        {
            "name": "Thyroid Stimulating Hormone (TSH)",
            "regex": re.compile(r"\b(tsh|thyroid\s+stimulating\s+hormone)\b[:\s\-]*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%]+)?", re.IGNORECASE),
            "typical_range": "0.4–4.0 mIU/L (Varies by laboratory and trimester)",
            "plain_explanation": "A pituitary hormone that regulates the thyroid gland's production of thyroxine (T4) and triiodothyronine (T3)."
        }
    ]

    @classmethod
    def extract_text_from_pdf(cls, file_stream: io.BytesIO) -> str:
        """Extracts text safely from an uploaded PDF stream."""
        try:
            reader = PdfReader(file_stream)
            if reader.is_encrypted:
                raise ValueError("The provided PDF report is password protected. Please provide an unencrypted document.")

            extracted_text = []
            max_pages = min(len(reader.pages), 10)
            for i in range(max_pages):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    extracted_text.append(page_text)

            combined = "\n".join(extracted_text).strip()
            if not combined:
                raise ValueError("No extractable digital text found in this PDF. It may be an image scan without an OCR text layer.")
            return combined
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise ValueError(f"Failed to process PDF report: {str(e)}")

    @classmethod
    def analyze_report_text(cls, raw_text: str) -> Dict[str, Any]:
        """
        Parses report text for known clinical biomarkers, extracts observed values,
        and provides plain language educational explanations.
        """
        if not raw_text or len(raw_text.strip()) < 5:
            return {
                "detected_markers": [],
                "raw_excerpt": "",
                "summary": "Report text was empty or too brief to identify laboratory metrics."
            }

        detected_markers: List[Dict[str, Any]] = []

        for marker in cls.KNOWN_LAB_MARKERS:
            match = marker["regex"].search(raw_text)
            if match:
                value_str = match.group(2)
                unit_str = match.group(3) or "standard unit"
                detected_markers.append({
                    "test_name": marker["name"],
                    "observed_value": f"{value_str} {unit_str}".strip(),
                    "typical_range": marker["typical_range"],
                    "plain_explanation": marker["plain_explanation"],
                    "clinical_note": "Reference ranges vary across laboratories and calibration standards. This value must be clinically interpreted in conjunction with your medical history and clinical exam."
                })

        # Generate summary
        if detected_markers:
            marker_list_str = ", ".join([m["test_name"] for m in detected_markers])
            summary = (
                f"Successfully parsed **{len(detected_markers)} laboratory biomarker(s)**: {marker_list_str}.\n\n"
                "Review the plain-language breakdowns below. Remember: isolated test values do not constitute a diagnosis and must be evaluated by your prescribing physician."
            )
        else:
            summary = (
                "No standard automated laboratory markers could be cleanly extracted from the provided text.\n"
                "Ensure the text includes standard test labels (e.g. Hemoglobin, Fasting Blood Sugar, HbA1c, Platelets, Creatinine)."
            )

        return {
            "detected_markers": detected_markers,
            "raw_excerpt": raw_text[:400] + ("..." if len(raw_text) > 400 else ""),
            "summary": summary
        }
