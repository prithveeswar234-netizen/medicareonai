"""
sample_reports_generator.py - Generates realistic medical lab report PDFs
for testing the 100% PDF-driven clinical analysis workflow.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "sample_reports")
os.makedirs(SAMPLE_DIR, exist_ok=True)


def build_sample_pdf(filename, hospital_name, patient_name, age_gender, tests, clinical_notes, suspected):
    filepath = os.path.join(SAMPLE_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    teal = colors.HexColor("#0f766e")
    dark = colors.HexColor("#1e293b")

    elements = []

    # Hospital Header
    header = [
        [
            Paragraph(f"<b>{hospital_name}</b><br/><font size='8' color='#64748b'>Accredited Diagnostic Pathology &amp; Clinical Laboratory</font>", styles['Normal']),
            Paragraph(f"<b>REPORT CODE:</b> LAB-{filename[:4].upper()}<br/><font size='8' color='#64748b'>Universal Health Standards Compliant</font>", styles['Normal'])
        ]
    ]
    t_head = Table(header, colWidths=[4.5 * inch, 2.8 * inch])
    elements.append(t_head)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=4, spaceAfter=8))

    # Patient Details Box
    p_box = [
        [Paragraph(f"<b>Patient Name:</b> {patient_name}", styles['Normal']), Paragraph(f"<b>Age/Gender:</b> {age_gender}", styles['Normal'])],
        [Paragraph("<b>Referred By:</b> Dr. AI Medicare, MD", styles['Normal']), Paragraph("<b>Sample Type:</b> Blood Plasma &amp; Vitals Biometrics", styles['Normal'])]
    ]
    t_pbox = Table(p_box, colWidths=[3.6 * inch, 3.7 * inch])
    t_pbox.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 5)
    ]))
    elements.append(t_pbox)
    elements.append(Spacer(1, 10))

    # Test Results Table
    elements.append(Paragraph("<b>LABORATORY INVESTIGATION &amp; OBSERVED VITALS</b>", styles['Normal']))
    elements.append(Spacer(1, 4))
    
    t_data = [["Investigation Parameter", "Observed Value", "Biological Reference Range", "Flag Status"]]
    for item in tests:
        t_data.append(item)

    t_table = Table(t_data, colWidths=[2.6 * inch, 1.6 * inch, 2.0 * inch, 1.1 * inch])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark)
    ]))
    elements.append(t_table)
    elements.append(Spacer(1, 10))

    # Doctor / Clinical Notes
    notes_html = f"""
    <b>CLINICAL SYMPTOM OBSERVATIONS &amp; PHYSICIAN REMARKS:</b><br/>
    {clinical_notes}<br/><br/>
    <b>PRIMARY CLINICAL IMPRESSION:</b> <font color='#b91c1c'><b>{suspected}</b></font>
    """
    t_notes = Table([[Paragraph(notes_html, styles['Normal'])]], colWidths=[7.3 * inch])
    t_notes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#f59e0b")),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    elements.append(t_notes)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<font size='8' color='#94a3b8'>* Laboratory verification signed by Senior Pathologist &amp; Dr. AI Medicare System.</font>", styles['Normal']))

    doc.build(elements)
    print(f"Generated sample report: {filepath}")
    return filepath


def generate_all_samples():
    # 1. Diabetic & Cardiovascular Risk Report
    build_sample_pdf(
        filename="Sample_Diabetic_Heart_Report.pdf",
        hospital_name="Dr. AI Medicare - Central Diagnostic Lab",
        patient_name="Alex Morgan",
        age_gender="52 Yrs / Male",
        tests=[
            ["Fasting Blood Glucose", "148.0 mg/dL", "70 - 99 mg/dL", "HIGH"],
            ["Glycated Hemoglobin (HbA1c)", "7.4 %", "< 5.7 %", "ELEVATED"],
            ["Systolic Blood Pressure", "146 mmHg", "< 120 mmHg", "HIGH"],
            ["Diastolic Blood Pressure", "94 mmHg", "< 80 mmHg", "HIGH"],
            ["Oxygen SpO2", "97.0 %", "95 - 100 %", "NORMAL"],
            ["Heart Rate", "84 bpm", "60 - 100 bpm", "NORMAL"],
            ["Body Mass Index (BMI)", "29.4 kg/m²", "18.5 - 24.9 kg/m²", "OVERWEIGHT"],
            ["Hemoglobin", "13.6 g/dL", "13.0 - 17.0 g/dL", "NORMAL"]
        ],
        clinical_notes="Patient presents with persistent polydipsia (excessive thirst), frequent nighttime urination (polyuria), chronic daytime fatigue, and intermittent exertional chest tightness. Lifestyle includes daily smoking and sedentary physical activity.",
        suspected="Type 2 Diabetes Mellitus with Stage 2 Hypertensive Cardiovascular Risk."
    )

    # 2. Viral Respiratory / Flu Infection Report
    build_sample_pdf(
        filename="Sample_Viral_Respiratory_Flu_Report.pdf",
        hospital_name="Dr. AI Medicare - Pulmonary & Infectious Diseases",
        patient_name="David Ross",
        age_gender="44 Yrs / Male",
        tests=[
            ["Oxygen Saturation (SpO2)", "93.0 %", "95 - 100 %", "LOW / HYPOXIA"],
            ["Body Temperature", "102.4 °F", "97.8 - 99.0 °F", "HIGH FEVER"],
            ["Heart Rate (Pulse)", "98 bpm", "60 - 100 bpm", "ELEVATED"],
            ["Systolic Blood Pressure", "122 mmHg", "< 120 mmHg", "NORMAL"],
            ["Diastolic Blood Pressure", "80 mmHg", "< 80 mmHg", "NORMAL"],
            ["Fasting Blood Glucose", "98.0 mg/dL", "70 - 99 mg/dL", "NORMAL"],
            ["Total Leukocyte Count (WBC)", "12,800 /uL", "4,500 - 11,000 /uL", "ELEVATED"],
            ["C-Reactive Protein (CRP)", "38.5 mg/L", "< 5.0 mg/L", "HIGH INFLAMMATION"]
        ],
        clinical_notes="Acute onset fever with severe chills, persistent intractable dry cough, bronchial irritation, muscle myalgia, and shortness of breath upon minimal exertion for 3 days. Throat congestion observed.",
        suspected="Acute Viral Respiratory Syndrome (Influenza / Viral Bronchopneumonia)."
    )

    # 3. Anemia & Fatigue Report
    build_sample_pdf(
        filename="Sample_Anemia_Fatigue_Report.pdf",
        hospital_name="Dr. AI Medicare - Hematology Lab",
        patient_name="Sarah Jenkins",
        age_gender="38 Yrs / Female",
        tests=[
            ["Hemoglobin", "9.2 g/dL", "12.0 - 15.5 g/dL", "CRITICAL LOW"],
            ["Red Blood Cell (RBC) Count", "3.2 mil/uL", "3.8 - 5.2 mil/uL", "LOW"],
            ["Serum Ferritin", "11.0 ng/mL", "20 - 200 ng/mL", "LOW"],
            ["Systolic Blood Pressure", "110 mmHg", "< 120 mmHg", "NORMAL"],
            ["Diastolic Blood Pressure", "72 mmHg", "< 80 mmHg", "NORMAL"],
            ["Fasting Blood Glucose", "89.0 mg/dL", "70 - 99 mg/dL", "NORMAL"],
            ["Oxygen SpO2", "98.0 %", "95 - 100 %", "NORMAL"],
            ["Heart Rate", "88 bpm", "60 - 100 bpm", "NORMAL"]
        ],
        clinical_notes="Patient complains of extreme debilitating chronic exhaustion, postural dizziness, pale conjunctiva, brittle nails, and cold intolerance. No diabetic or cardiac history.",
        suspected="Microcytic Hypochromic Iron Deficiency Anemia."
    )


if __name__ == "__main__":
    generate_all_samples()
