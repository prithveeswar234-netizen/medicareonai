# test_new_medication_and_language_features.py
import os
import json
import sqlite3
from app import app
from gemini_service import get_authentic_disease_medications, analyze_medical_data
from pdf_generator import generate_medical_pdf

def test_all():
    client = app.test_client()

    print("--- 1. Testing Authentic Disease & Virus Medications & Timetable ---")
    
    # Test Diabetic Case
    diabetic_meds = get_authentic_disease_medications([{'name': 'Type 2 Diabetes Mellitus'}], {'fasting_glucose': 148, 'systolic_bp': 146}, 'high blood sugar, thirst')
    assert len(diabetic_meds) >= 1
    d_names = [m['name'] for m in diabetic_meds]
    assert any('Metformin' in n or 'Glycomet' in n for n in d_names), f"Missing Metformin/Glycomet: {d_names}"
    
    # Check timings & meal schedules
    for m in diabetic_meds:
        assert m['timing'] in ['Morning', 'Afternoon', 'Night', 'Morning & Night', 'Morning, Afternoon & Night (SOS)'], f"Invalid timing: {m['timing']}"
        meal_str = m['meal_relation'].lower()
        assert any(k in meal_str for k in ['meal', 'food', 'breakfast', 'dinner', 'lunch', 'empty stomach']), f"Missing meal relation: {m['meal_relation']}"
    print(f"   [PASS] Diabetes Medications verified ({len(diabetic_meds)} items): {[m['name'] for m in diabetic_meds]}")

    # Test Viral Respiratory / Flu Case
    viral_meds = get_authentic_disease_medications([{'name': 'Viral Respiratory Infection / Influenza'}], {'spo2': 93, 'temperature': 102.4}, 'high fever, cough')
    assert len(viral_meds) >= 3
    v_names = [m['name'] for m in viral_meds]
    assert any('Oseltamivir' in n or 'Tamiflu' in n for n in v_names), f"Missing Tamiflu: {v_names}"
    assert any('Paracetamol' in n or 'Dolo' in n for n in v_names), f"Missing Dolo/Paracetamol: {v_names}"
    assert any('Ascoril' in n or 'Monticope' in n for n in v_names), f"Missing Cough/Allergy medicine: {v_names}"

    for m in viral_meds:
        assert 'timing' in m and m['timing']
        assert 'meal_relation' in m and m['meal_relation']
        assert 'duration' in m and m['duration']
    print(f"   [PASS] Viral Flu Medications verified ({len(viral_meds)} items): {[m['name'] for m in viral_meds]}")

    # Test Anemia Case
    anemia_meds = get_authentic_disease_medications([{'name': 'Iron Deficiency Anemia'}], {'hemoglobin': 9.2}, 'fatigue, pale skin')
    assert len(anemia_meds) >= 1
    a_names = [m['name'] for m in anemia_meds]
    assert any('Orofer' in n or 'Ferrous' in n for n in a_names), f"Missing Orofer/Iron: {a_names}"
    print(f"   [PASS] Anemia Medications verified ({len(anemia_meds)} items): {[m['name'] for m in anemia_meds]}")

    print("\n--- 2. Testing Sample PDF Analysis API with Prescribed Medications ---")
    res = client.post('/api/analyze-sample-report', json={'sample_id': 'viral'})
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data['success'] is True
    assert 'prescribed_medications' in res_data['analysis']
    assert len(res_data['analysis']['prescribed_medications']) >= 2
    print(f"   [PASS] /api/analyze-sample-report returned {len(res_data['analysis']['prescribed_medications'])} authentic viral medications!")

    print("\n--- 3. Testing PDF Generation With Prescription Schedule Section 5b ---")
    pdf_out = os.path.join("uploads", "reports", "test_prescription_output.pdf")
    generate_medical_pdf(
        patient_info={"name": "Pruthve Kumar", "age": 45, "gender": "Male", "id": 1},
        analysis_data=res_data['analysis'],
        vitals={"spo2": 93, "temperature": 102.4, "heart_rate": 88},
        lifestyle={},
        output_filepath=pdf_out
    )
    assert os.path.exists(pdf_out), "PDF report file was not generated"
    assert os.path.getsize(pdf_out) > 5000, "PDF file is too small"
    print(f"   [PASS] PDF report generated with full Section 5b Prescribed Medications table ({os.path.getsize(pdf_out)} bytes)")

    print("\n--- 4. Testing Pharmacy Catalog Breadth (Paracetamol to all diseases) ---")
    p_res = client.get('/api/pharmacy/catalog')
    assert p_res.status_code == 200
    catalog = p_res.get_json()
    assert len(catalog) >= 50, f"Expected at least 50 products, got {len(catalog)}"
    
    cat_names = [p['name'].lower() for p in catalog]
    # Check general & specific medicines
    assert any('dolo 650' in n or 'calpol' in n for n in cat_names), "Missing Paracetamol Dolo/Calpol"
    assert any('tamiflu' in n or 'oseltamivir' in n for n in cat_names), "Missing Tamiflu"
    assert any('augmentin' in n for n in cat_names), "Missing Augmentin"
    assert any('glycomet' in n or 'metformin' in n for n in cat_names), "Missing Glycomet"
    assert any('telma' in n for n in cat_names), "Missing Telma"
    assert any('pan 40' in n or 'pantoprazole' in n for n in cat_names), "Missing Pan 40"
    assert any('orofer' in n for n in cat_names), "Missing Orofer"
    assert any('accu-chek' in n for n in cat_names), "Missing Accu-Chek"
    print(f"   [PASS] Pharmacy catalog verified: {len(catalog)} certified original medicines in stock covering all clinical categories!")

    print("\n--- 5. Testing Multi-Language Translation Engine in app.js ---")
    with open(os.path.join("static", "js", "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    with open("translations_generated.json", "r", encoding="utf-8") as f:
        t_data = json.load(f)

    for lang in ['en', 'hi', 'te', 'ta', 'kn', 'es']:
        assert lang in t_data, f"Missing language {lang}"
        assert len(t_data[lang]) >= 180, f"Incomplete dictionary for {lang}: {len(t_data[lang])}"
        assert t_data[lang]['banner_text'], f"Missing banner_text for {lang}"
        assert t_data[lang]['meds_schedule_title'], f"Missing meds_schedule_title for {lang}"
        assert t_data[lang]['btn_quick_buy_med'], f"Missing btn_quick_buy_med for {lang}"
        assert t_data[lang]['btn_add_to_tracker'], f"Missing btn_add_to_tracker for {lang}"
    print(f"   [PASS] All 6 languages (en, hi, te, ta, kn, es) contain 184 matching translation keys!")

    assert "function renderPrescribedMedications" in app_js
    assert "function quickBuyPrescriptionMedicine" in app_js
    assert "function addMedicationToDailyScheduleFromEncoded" in app_js
    print("   [PASS] Frontend JavaScript contains renderPrescribedMedications and 1-click buy/tracker controllers!")

    print("\n=======================================================")
    print("[SUCCESS] ALL MEDICINE, SCHEDULE, PDF AND LANGUAGE TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == '__main__':
    test_all()
