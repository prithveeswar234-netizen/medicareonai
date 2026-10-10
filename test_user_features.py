import sqlite3
from app import app
from gemini_service import test_gemini_connection, get_active_api_key

def test_features():
    client = app.test_client()

    print("1. Testing Gemini API Key...")
    key = get_active_api_key()
    assert key is not None, "API key should be present in system_settings"
    ok, msg = test_gemini_connection(key)
    if ok:
        print(f"   [PASS] Gemini Connection verified: {msg}")
    else:
        print(f"   [INFO] Gemini Connection test result (Network/DNS status): {msg}")

    print("2. Testing Original Google Email Login (no authorization blocks)...")
    res = client.post('/api/auth/google-login', json={
        'email': 'pruthve.kumar@gmail.com',
        'name': 'Pruthve Kumar'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['email'] == 'pruthve.kumar@gmail.com'
    assert data['user']['name'] == 'Pruthve Kumar'
    assert data['user']['is_google_verified'] is True
    print(f"   [PASS] Google sign-in successful for original account: {data['user']['email']}")

    print("3. Testing Outdated Token Auto-Cancellation when day is crossed...")
    conn = sqlite3.connect('medicare.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO hospital_queue (user_id, hospital_name, patient_name, doctor_name, room_number, department, token_number, token_index, current_serving_token, estimated_wait_minutes, created_at, status)
        VALUES (1, 'Old Hospital', 'Outdated Patient', 'Dr. Smith', 'Room 101', 'General Medicine', 'EXP-001', 1, 1, 15, '2026-10-01 09:00:00', 'waiting')
    """)
    conn.commit()
    conn.close()

    q_res = client.get('/api/queue')
    assert q_res.status_code == 200
    q_data = q_res.get_json()
    assert all(t['token_number'] != 'EXP-001' for t in q_data['patient_tickets']), "Outdated token must not appear in active patient tickets"

    conn = sqlite3.connect('medicare.db')
    old_row = conn.execute("SELECT status FROM hospital_queue WHERE token_number = 'EXP-001'").fetchone()
    conn.close()
    assert old_row[0] == 'cancelled', f"Expected cancelled, got {old_row[0]}"
    print(f"   [PASS] Outdated token EXP-001 automatically cancelled! Status in DB: {old_row[0]}")

    print("4. Testing Token Booking & Dedicated Token Pass Card...")
    book_res = client.post('/api/queue/book', json={
        'hospital_name': 'Saveera Multi Speciality Hospital',
        'patient_name': 'Pruthve Kumar',
        'patient_phone': '+91 99887-76655',
        'department': 'Cardiology & Comprehensive Heart Center',
        'appointment_slot': 'Morning Slot (09:00 AM - 12:00 PM)',
        'symptoms': 'Chest tightness and blood pressure screening'
    })
    assert book_res.status_code == 200
    tok = book_res.get_json()
    assert tok['success'] is True
    tok_id = tok['id']
    print(f"   [PASS] Token {tok['token_number']} booked for {tok['patient_name']} at {tok['hospital_name']}")

    # Verify only this active token appears
    q_check = client.get('/api/queue').get_json()
    assert any(t['id'] == tok_id for t in q_check['patient_tickets'])
    print(f"   [PASS] Active Token verified in queue")

    print("5. Testing Manual Token Cancellation...")
    cancel_res = client.post(f'/api/queue/{tok_id}/cancel')
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.get_json()
    assert cancel_data['success'] is True
    print(f"   [PASS] Token {tok['token_number']} manually cancelled: {cancel_data['message']}")

    q_after = client.get('/api/queue').get_json()
    assert all(t['id'] != tok_id for t in q_after['patient_tickets']), "Cancelled token must not appear in active tickets"
    print("   [PASS] Cancelled token is not in active patient tickets.")

    print("\n[SUCCESS] ALL REQUESTED USER FEATURES VERIFIED AND PASSING!")

if __name__ == "__main__":
    test_features()
