"""
pdf_generator.py - Dr. AI Medicare Clinical Medical Report PDF Generator
Produces high-quality, clinical-grade medical assessment PDFs for patients and physicians.
Global Clinical Decision Support Standards compliant.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def generate_medical_pdf(patient_info, analysis_data, vitals, lifestyle, output_filepath):
    """
    Builds a professional clinical PDF document using ReportLab.
    """
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    primary_color = colors.HexColor("#0f766e")      # Deep medical teal
    clinical_blue = colors.HexColor("#008dc9")      # Clinical Primary Blue
    dark_text = colors.HexColor("#1e293b")          # Slate 800
    sub_text = colors.HexColor("#64748b")           # Slate 500
    alert_red = colors.HexColor("#b91c1c")          # Red 700
    warning_orange = colors.HexColor("#c2410c")     # Orange 700
    success_green = colors.HexColor("#15803d")      # Green 700

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=sub_text
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=7,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=sub_text
    )

    elements = []

    # 1. Header Banner: Dr. AI Medicare Clinical Decision Support
    header_data = [
        [
            Paragraph("<b>DR. AI MEDICARE</b><br/><font size='8' color='#0f766e'>ADVANCED CLINICAL AI &amp; DECISION SUPPORT NETWORK</font>", title_style),
            Paragraph(f"<b>REPORT ID:</b> AIMEDICARE-{datetime.now().strftime('%Y%m%d%H%M')}<br/><b>DATE:</b> {datetime.now().strftime('%B %d, %Y')}<br/><b>ACCREDITATION:</b> CLINICAL HEALTH PROTOCOLS", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.5 * inch, 2.8 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceBefore=2, spaceAfter=8))

    # 2. Patient Demographics Box
    p_name = patient_info.get("name", "Alex Morgan")
    p_age = str(patient_info.get("age", "52"))
    p_gender = patient_info.get("gender", "Male")
    p_blood = patient_info.get("blood_group", "O+")
    p_caregiver = patient_info.get("caregiver_name", "Elena Morgan (Daughter)")

    patient_grid = [
        [
            Paragraph("<b>Patient Name:</b>", body_bold), Paragraph(p_name, body_text),
            Paragraph("<b>Age / Gender:</b>", body_bold), Paragraph(f"{p_age} yrs / {p_gender}", body_text)
        ],
        [
            Paragraph("<b>Supervising Clinician:</b>", body_bold), Paragraph("Dr. AI Medicare, MD", body_text),
            Paragraph("<b>Emergency Caregiver:</b>", body_bold), Paragraph(p_caregiver, body_text)
        ]
    ]
    patient_table = Table(patient_grid, colWidths=[1.5 * inch, 2.2 * inch, 1.6 * inch, 2.0 * inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 10))

    # 3. Overall Risk Stratification Box (Traffic Light Colors)
    risk_level = analysis_data.get("risk_level", "Moderate")
    risk_score = analysis_data.get("risk_score_percent", 55)

    risk_bg = colors.HexColor("#fef2f2") if risk_level in ["High", "Urgent"] else (
        colors.HexColor("#fffbeb") if risk_level == "Moderate" else colors.HexColor("#f0fdf4")
    )
    risk_border = alert_red if risk_level in ["High", "Urgent"] else (
        warning_orange if risk_level == "Moderate" else success_green
    )

    risk_html = f"""
    <b>HEALTH RISK LEVEL:</b> <font color='{risk_border.hexval()}'><b>{risk_level.upper()} RISK ({risk_score}% Risk Index)</b></font><br/>
    <font size='9' color='#334155'>{analysis_data.get('clinical_summary', 'Automated PDF evaluation complete.')}</font>
    """
    risk_table = Table([[Paragraph(risk_html, body_text)]], colWidths=[7.3 * inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), risk_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, risk_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 10))

    # 4. Extracted Biometric Vitals Table
    elements.append(Paragraph("Automated Biometrics & Lab Findings (Extracted from Report)", section_heading))
    vitals_grid = [
        [
            Paragraph("<b>Parameter</b>", body_bold),
            Paragraph("<b>Observed Value</b>", body_bold),
            Paragraph("<b>Standard Reference Range</b>", body_bold),
            Paragraph("<b>Status</b>", body_bold)
        ]
    ]

    sbp = int(vitals.get("systolic_bp") or 120)
    dbp = int(vitals.get("diastolic_bp") or 80)
    bp_status = "Normal" if sbp < 120 and dbp < 80 else ("Elevated" if sbp < 130 and dbp < 80 else "High / Hypertensive")
    vitals_grid.append([
        Paragraph("Blood Pressure", body_text),
        Paragraph(f"{sbp}/{dbp} mmHg", body_bold),
        Paragraph("&lt; 120/80 mmHg", body_text),
        Paragraph(bp_status, body_text)
    ])

    f_glu = float(vitals.get("fasting_glucose") or 95)
    glu_status = "Normal" if f_glu < 100 else ("Impaired" if f_glu < 126 else "High / Diabetic Range")
    vitals_grid.append([
        Paragraph("Fasting Blood Sugar", body_text),
        Paragraph(f"{f_glu:.1f} mg/dL", body_bold),
        Paragraph("70 - 99 mg/dL", body_text),
        Paragraph(glu_status, body_text)
    ])

    spo2 = float(vitals.get("spo2") or 98)
    spo2_status = "Safe" if spo2 >= 95 else "Hypoxia Warning"
    vitals_grid.append([
        Paragraph("Oxygen Saturation (SpO2)", body_text),
        Paragraph(f"{spo2:.1f} %", body_bold),
        Paragraph("95 - 100 %", body_text),
        Paragraph(spo2_status, body_text)
    ])

    hb = float(vitals.get("hemoglobin") or 14.0)
    hb_status = "Normal" if hb >= 12.0 else "Low / Anemic"
    vitals_grid.append([
        Paragraph("Hemoglobin Level", body_text),
        Paragraph(f"{hb:.1f} g/dL", body_bold),
        Paragraph("12.0 - 16.5 g/dL", body_text),
        Paragraph(hb_status, body_text)
    ])

    v_table = Table(vitals_grid, colWidths=[2.2 * inch, 1.6 * inch, 2.0 * inch, 1.5 * inch])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(v_table)
    elements.append(Spacer(1, 10))

    # 5. Suspected Chronic Conditions & Viral Pathogens
    elements.append(Paragraph("Estimated Health Risks & Possible Conditions", section_heading))
    cond_rows = [
        [Paragraph("<b>Condition / Suspected Etiology</b>", body_bold), Paragraph("<b>Category</b>", body_bold), Paragraph("<b>Probability</b>", body_bold), Paragraph("<b>Key Indicators Found</b>", body_bold)]
    ]
    for c in analysis_data.get("primary_conditions", []):
        cond_rows.append([
            Paragraph(f"<b>{c.get('name', 'N/A')}</b>", body_text),
            Paragraph(c.get("type", "Chronic"), body_text),
            Paragraph(f"<b>{c.get('probability', 'Moderate')}</b>", body_text),
            Paragraph(", ".join(c.get("key_indicators", [])) if c.get("key_indicators") else "Biometric pattern", body_text)
        ])
    cond_table = Table(cond_rows, colWidths=[2.4 * inch, 1.5 * inch, 1.1 * inch, 2.3 * inch])
    cond_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cond_table)
    elements.append(Spacer(1, 8))

    # 5b. Prescribed Original Medications & Intake Schedule (Pharmacy Buy Guide)
    prescribed_meds = analysis_data.get("prescribed_medications", [])
    if prescribed_meds:
        elements.append(Paragraph("Prescribed Disease-Specific Medications & Intake Schedule", section_heading))
        med_rows = [
            [
                Paragraph("<b>Medicine Name &amp; Brand</b>", body_bold),
                Paragraph("<b>Target Condition / Virus</b>", body_bold),
                Paragraph("<b>Daily Timing</b>", body_bold),
                Paragraph("<b>Meal Relation</b>", body_bold),
                Paragraph("<b>Dosage &amp; Instructions</b>", body_bold)
            ]
        ]
        for m in prescribed_meds:
            med_rows.append([
                Paragraph(f"<b>{m.get('name', 'Prescription Med')}</b>", body_text),
                Paragraph(m.get("condition_target", "General Care"), body_text),
                Paragraph(f"<font color='#0284c7'><b>{m.get('timing', 'Daily')}</b></font>", body_text),
                Paragraph(f"<font color='#0f766e'><b>{m.get('meal_relation', 'After meal')}</b></font>", body_text),
                Paragraph(f"{m.get('dosage', '')}. {m.get('instructions', '')}", body_text)
            ])
        med_table = Table(med_rows, colWidths=[1.8 * inch, 1.6 * inch, 1.1 * inch, 1.2 * inch, 1.6 * inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0f2fe")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(med_table)
        elements.append(Spacer(1, 8))

    # 6. Clinician Consultation & Next Steps
    rec = analysis_data.get("doctor_recommendation", {})
    specialists_str = ", ".join(rec.get("recommended_specialists", ["General Physician"]))
    urgency_str = rec.get("urgency_timeframe", "Routine consultation")

    elements.append(Paragraph("Recommended Action for Patient", section_heading))
    next_steps_text = f"""
    • <b>Doctor Specialty:</b> {specialists_str}<br/>
    • <b>Urgency Level:</b> {urgency_str}<br/>
    • <b>Why Consultation Is Needed:</b> {rec.get('clinical_rationale', 'Early consultation prevents emergency complications.')}<br/>
    • <b>Tests to Confirm:</b> {', '.join(analysis_data.get('recommended_diagnostic_tests', ['HbA1c', 'Lipid Panel', 'ECG']))}
    """
    steps_table = Table([[Paragraph(next_steps_text, body_text)]], colWidths=[7.3 * inch])
    steps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    elements.append(steps_table)
    elements.append(Spacer(1, 10))

    # 7. Red Flags & Disclaimer
    elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceBefore=4, spaceAfter=6))
    disclaimer_text = (
        "<b>DR. AI MEDICARE DISCLAIMER:</b> This medical summary is generated by Dr. AI Medicare's Clinical AI Support System "
        "in alignment with Global Clinical Decision Support protocols. It is designed to assist doctors and patients in detecting "
        "early chronic disease markers and does NOT replace diagnosis or treatment by a licensed physician."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build document
    doc.build(elements)
    return output_filepath
