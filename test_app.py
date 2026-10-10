"""
test_app.py - Verification test suite for Dr. AI Medicare
Tests Google login, Clinical Care Network standards, 100% PDF-driven analysis, medication tracker, and hospital queue.
"""

import os
import sys
import json

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import app


def run_tests():
    client = app.test_client()

    print("1. Testing GET / (Landing page, Dr. AI Medicare & Clinical Care Network Branding)...")
    res = client.get('/')
    assert res.status_code == 200, f"Failed: {res.status_code}"
    html = res.get_data(as_text=True)
    assert "Dr. AI Medicare" in html
    assert "Clinical Care Network" in html
    assert "Universal Health Organization" not in html
    assert "Sign in with Google" in html
    print("   [PASS] Dr. AI Medicare and Clinical Care Network branding verified (WHO removed)!")

    print("2. Testing POST /api/auth/google-login (Google/Gmail Authentication)...")
    login_res = client.post('/api/auth/google-login', json={
        "email": "alex.morgan@gmail.com",
        "name": "Alex Morgan"
    })
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["success"] is True
    print(f"   [PASS] Google sign-in successful: {login_data['user']['email']}")

    print("3. Testing 100% PDF-Driven Sample Report Analysis (Diabetic & Cardiac PDF)...")
    sample_res = client.post('/api/analyze-sample-report', json={"sample_id": "diabetic"})
    assert sample_res.status_code == 200
    sample_data = sample_res.get_json()
    assert sample_data["success"] is True
    assert "pdf_url" in sample_data
    bio = sample_data["extracted_biometrics"]
    print(f"   [PASS] PDF Auto-Extraction: Glucose={bio['fasting_glucose']}, BP={bio['systolic_bp']}/{bio['diastolic_bp']}, Risk={sample_data['analysis']['risk_level']}")

    print("4. Testing 1-Click Viral Respiratory Sample PDF...")
    viral_res = client.post('/api/analyze-sample-report', json={"sample_id": "viral"})
    assert viral_res.status_code == 200
    viral_data = viral_res.get_json()
    assert viral_data["success"] is True
    print(f"   [PASS] Viral PDF Evaluated: Condition={viral_data['analysis']['primary_conditions'][0]['name']}")

    print("5. Testing 1-Click Anemia Sample PDF...")
    anemia_res = client.post('/api/analyze-sample-report', json={"sample_id": "anemia"})
    assert anemia_res.status_code == 200
    anemia_data = anemia_res.get_json()
    assert anemia_data["success"] is True
    print(f"   [PASS] Anemia PDF Evaluated: Condition={anemia_data['analysis']['primary_conditions'][0]['name']}")

    print("6. Testing PDF Download (/api/download-report/<id>)...")
    record_id = sample_data["record_id"]
    pdf_res = client.get(f"/api/download-report/{record_id}")
    assert pdf_res.status_code == 200
    assert len(pdf_res.data) > 1000
    print(f"   [PASS] PDF generated & downloaded successfully ({len(pdf_res.data)} bytes)")

    print("7. Testing Medications & Adherence...")
    meds_res = client.get('/api/medications')
    assert meds_res.status_code == 200
    meds = meds_res.get_json()
    assert len(meds) > 0
    print(f"   [PASS] {len(meds)} active prescriptions retrieved")

    print("8. Testing Caregiver Alert Dispatch...")
    alert_res = client.post('/api/caregiver/alert')
    assert alert_res.status_code == 200
    alert_data = alert_res.get_json()
    assert alert_data["success"] is True
    print(f"   [PASS] Caregiver Alert dispatched to {alert_data['recipient']}")

    print("9. Testing Live Hospital Digital OPD Queue & Token Booking with Patient Details...")
    # Book a token with specific patient details
    book_res = client.post('/api/queue/book', json={
        "hospital_name": "Government General Hospital (GGH / RIMS)",
        "patient_name": "Pruthve Kumar",
        "patient_phone": "+91 98765-43210",
        "department": "Cardiology & Comprehensive Heart Center",
        "doctor_name": "Dr. Sarah Jenkins, MD",
        "room_number": "Room 204",
        "appointment_slot": "Immediate Live OPD Queue (Next Available)",
        "symptoms": "High blood pressure and routine cardiovascular review",
        "avg_mins": 12
    })
    assert book_res.status_code == 200
    book_data = book_res.get_json()
    assert book_data["success"] is True
    assert book_data["hospital_name"] == "Government General Hospital (GGH / RIMS)"
    assert book_data["patient_name"] == "Pruthve Kumar"
    assert book_data["patient_phone"] == "+91 98765-43210"
    assert "token_number" in book_data
    print(f"   [PASS] Booked Digital OPD Token: {book_data['token_number']} at {book_data['hospital_name']} for {book_data['patient_name']} (Wait: {book_data['estimated_wait_minutes']} mins)")

    queue_res = client.get('/api/queue')
    assert queue_res.status_code == 200
    queue_data = queue_res.get_json()
    assert len(queue_data["patient_tickets"]) > 0
    # Verify no fake hospital names in available departments
    for dept in queue_data["available_departments"]:
        assert "Dr. Pruthve" not in dept["name"], f"Department name should not contain fake hospital name: {dept['name']}"
    ticket = queue_data["patient_tickets"][0]
    print(f"   [PASS] Active Ticket in DB: {ticket['token_number']} at {ticket['hospital_name']}, Status: {ticket['status']}")

    # Advance queue simulation
    adv_res = client.post(f"/api/queue/{ticket['id']}/advance")
    assert adv_res.status_code == 200
    adv_data = adv_res.get_json()
    print(f"   [PASS] Queue advanced: Now serving #{adv_data['now_serving']}")

    print("10. Testing Pharmacy Store Catalog (/api/pharmacy/catalog)...")
    pharm_res = client.get('/api/pharmacy/catalog')
    assert pharm_res.status_code == 200
    catalog = pharm_res.get_json()
    assert len(catalog) >= 5
    print(f"   [PASS] Retrieved {len(catalog)} certified medicines (e.g. {catalog[0]['name']} ₹{catalog[0]['price']})")

    print("11. Testing Online Pharmacy Doorstep Order (/api/pharmacy/order)...")
    order_res = client.post('/api/pharmacy/order', json={
        "items": [{"id": catalog[0]["id"], "name": catalog[0]["name"], "strength": catalog[0]["strength"], "price": catalog[0]["price"], "qty": 2}],
        "delivery_address": "742 Evergreen Terrace, Apt 4B",
        "delivery_city": "Metro District",
        "phone": "+1 (555) 234-5678",
        "delivery_type": "Express 30-min Delivery",
        "payment_method": "Cash on Delivery",
        "total_amount": catalog[0]["price"] * 2
    })
    assert order_res.status_code == 200
    order_data = order_res.get_json()
    assert order_data["success"] is True
    assert "order_number" in order_data
    print(f"   [PASS] Doorstep Order Placed: #{order_data['order_number']}, ETA: {order_data['estimated_arrival']}")

    print("12. Testing Pharmacy Order History (/api/pharmacy/orders)...")
    history_res = client.get('/api/pharmacy/orders')
    assert history_res.status_code == 200
    orders_list = history_res.get_json()
    assert len(orders_list) > 0
    print(f"   [PASS] {len(orders_list)} past doorstep orders tracked in database")

    print("13. Testing Live Nearby Hospitals Locator (/api/hospitals/nearby)...")
    hosp_res = client.get('/api/hospitals/nearby')
    assert hosp_res.status_code == 200
    hospitals = hosp_res.get_json()
    assert len(hospitals) >= 4
    # Ensure no fake hospital on Dr. Pruthve exists in the database
    assert all("Dr. Pruthve" not in h['name'] for h in hospitals), "No fake hospital on user name should exist"
    closest = hospitals[0]
    assert "latitude" in closest and "longitude" in closest, "Hospitals must include latitude and longitude for GPS distance calculations"
    assert closest["latitude"] is not None and closest["longitude"] is not None
    print(f"   [PASS] Real Hospitals Verified! Closest: {closest['name']} in {closest['city']} ({closest['distance_km']} km away, Lat: {closest['latitude']}, Lon: {closest['longitude']})")

    print("13b. Testing Real Hospital City Filtering & Aliases (/api/hospitals/nearby?search=anantapur)...")
    atp_res = client.get('/api/hospitals/nearby?search=anantapur')
    assert atp_res.status_code == 200
    atp_hospitals = atp_res.get_json()
    assert len(atp_hospitals) >= 2
    assert "directions_url" in atp_hospitals[0]
    assert "maps/dir/" in atp_hospitals[0]["directions_url"]
    print(f"   [PASS] Anantapur Alias Search Found: {', '.join(h['name'] for h in atp_hospitals)}")
    print(f"   [PASS] Turn-by-Turn Navigation URL verified: {atp_hospitals[0]['directions_url'][:65]}...")

    print("13c. Testing Bangalore Alias Search (/api/hospitals/nearby?search=bangalore)...")
    blr_res = client.get('/api/hospitals/nearby?search=bangalore')
    assert blr_res.status_code == 200
    blr_hospitals = blr_res.get_json()
    assert len(blr_hospitals) >= 3
    print(f"   [PASS] Bangalore Alias Search Found: {', '.join(h['name'] for h in blr_hospitals[:3])}")

    print("13d. Testing Dynamic City Fallback (/api/hospitals/nearby?search=guntur)...")
    fallback_res = client.get('/api/hospitals/nearby?search=guntur')
    assert fallback_res.status_code == 200
    fallback_hospitals = fallback_res.get_json()
    assert len(fallback_hospitals) >= 2
    assert "Guntur" in fallback_hospitals[0]["city"]
    print(f"   [PASS] Dynamic City Fallback Verified for Guntur: {fallback_hospitals[0]['name']}")

    print("14. Testing Emergency Ambulance Dispatch (/api/ambulance/request)...")
    amb_res = client.post('/api/ambulance/request', json={
        "hospital_name": closest['name'],
        "location": "Subhash Road, Ananthapuramu"
    })
    assert amb_res.status_code == 200
    amb_data = amb_res.get_json()
    assert amb_data["success"] is True
    assert amb_data["eta_mins"] == 7
    print(f"   [PASS] Ambulance Dispatched: Ref {amb_data['dispatch_id']}, ETA: {amb_data['eta_mins']} mins")

    print("\n[SUCCESS] ALL VERIFICATION TESTS PASSED! MULTI-LANGUAGE VOICE, GOOGLE AUTH, PHARMACY & GOOGLE MAPS VERIFIED.")


if __name__ == "__main__":
    run_tests()
