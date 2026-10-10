"""
database.py - SQLite database management for Dr. AI Medicare
Handles users, medical health records, medications, adherence logs,
pharmacy store products, doorstep orders, and live nearby hospital locations.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medicare.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        age INTEGER,
        gender TEXT,
        blood_group TEXT,
        caregiver_name TEXT,
        caregiver_phone TEXT,
        caregiver_email TEXT,
        medical_history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Health Analysis Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        report_filename TEXT,
        symptoms TEXT,
        vitals_json TEXT,
        lifestyle_json TEXT,
        extracted_text TEXT,
        risk_level TEXT,
        primary_condition TEXT,
        ai_analysis_json TEXT,
        doctor_recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 3. Medications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        scheduled_time TEXT NOT NULL,
        instructions TEXT,
        condition_target TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 4. Medication Adherence Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adherence_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medication_id INTEGER,
        user_id INTEGER,
        date TEXT NOT NULL,
        status TEXT NOT NULL, /* 'taken', 'missed', 'pending' */
        taken_at TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (medication_id) REFERENCES medications (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 5. Pharmacy Medicines Catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pharmacy_medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        strength TEXT NOT NULL,
        category TEXT NOT NULL,
        form TEXT NOT NULL, /* 'Tablets', 'Capsules', 'Inhaler', 'Syrup', 'Device' */
        price REAL NOT NULL,
        discount_price REAL NOT NULL,
        stock_status TEXT DEFAULT 'In Stock',
        description TEXT,
        rx_required INTEGER DEFAULT 0
    )
    """)

    # 6. Pharmacy Doorstep Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pharmacy_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_number TEXT UNIQUE NOT NULL,
        items_json TEXT NOT NULL,
        total_amount REAL NOT NULL,
        delivery_address TEXT NOT NULL,
        delivery_city TEXT NOT NULL,
        phone TEXT NOT NULL,
        delivery_type TEXT DEFAULT 'Express 30-min Delivery',
        payment_method TEXT DEFAULT 'Cash on Delivery',
        status TEXT DEFAULT 'Confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # 7. Live Nearby Hospitals Directory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals_directory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        distance_km REAL NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        phone TEXT NOT NULL,
        emergency_wait_mins INTEGER DEFAULT 10,
        icu_beds INTEGER DEFAULT 12,
        general_beds INTEGER DEFAULT 45,
        rating REAL DEFAULT 4.8,
        is_open_24_7 INTEGER DEFAULT 1,
        latitude REAL DEFAULT 14.6819,
        longitude REAL DEFAULT 77.6006
    )
    """)

    # 7b. Live Hospital Digital OPD Queue
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospital_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        hospital_name TEXT DEFAULT 'Government General Hospital (GGH / RIMS)',
        patient_name TEXT NOT NULL,
        patient_phone TEXT DEFAULT '+91 98765-43210',
        department TEXT NOT NULL,
        doctor_name TEXT DEFAULT 'Dr. Senior Clinical Consultant',
        room_number TEXT DEFAULT 'Room 102',
        appointment_slot TEXT DEFAULT 'Morning Slot (09:00 AM - 12:00 PM)',
        symptoms TEXT DEFAULT 'General consultation',
        token_number TEXT UNIQUE NOT NULL,
        token_index INTEGER DEFAULT 1,
        current_serving_token INTEGER DEFAULT 1,
        avg_consult_minutes INTEGER DEFAULT 10,
        estimated_wait_minutes INTEGER DEFAULT 15,
        status TEXT DEFAULT 'waiting',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Column migrations if tables already exist
    try:
        cursor.execute("ALTER TABLE hospitals_directory ADD COLUMN latitude REAL DEFAULT 14.6819")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hospitals_directory ADD COLUMN longitude REAL DEFAULT 77.6006")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hospital_queue ADD COLUMN hospital_name TEXT DEFAULT 'Government General Hospital (GGH / RIMS)'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hospital_queue ADD COLUMN patient_phone TEXT DEFAULT '+91 98765-43210'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hospital_queue ADD COLUMN appointment_slot TEXT DEFAULT 'Morning Slot (09:00 AM - 12:00 PM)'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hospital_queue ADD COLUMN symptoms TEXT DEFAULT 'General consultation'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'google'")
    except Exception:
        pass

    # 8. System Settings (API Keys, Configurations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Seed Default Data
    seed_default_data(conn)
    conn.close()


def seed_default_data(conn):
    cursor = conn.cursor()

    # Seed demo user if no user exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO users (name, email, phone, age, gender, blood_group, caregiver_name, caregiver_phone, caregiver_email, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Alex Morgan",
            "alex.morgan@gmail.com",
            "+1 (555) 234-5678",
            52,
            "Male",
            "O+",
            "Elena Morgan (Daughter)",
            "+1 (555) 987-6543",
            "elena.morgan@email.com",
            "Family history of Type 2 Diabetes, Borderline Hypertension"
        ))
        user_id = cursor.lastrowid

        # Seed sample medications
        sample_meds = [
            ("Metformin", "500 mg", "Twice Daily", "08:00 AM", "Take with breakfast", "Blood Glucose Regulation"),
            ("Lisinopril", "10 mg", "Once Daily", "09:00 AM", "Take in morning with water", "Blood Pressure Control"),
            ("Atorvastatin", "20 mg", "Once Daily", "09:00 PM", "Take at bedtime", "Cholesterol Management"),
            ("Vitamin D3", "2000 IU", "Once Daily", "01:00 PM", "Take with lunch", "Bone & Immune Health")
        ]
        today_str = datetime.now().strftime("%Y-%m-%d")

        for med in sample_meds:
            cursor.execute("""
            INSERT INTO medications (user_id, name, dosage, frequency, scheduled_time, instructions, condition_target)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, med[0], med[1], med[2], med[3], med[4], med[5]))
            med_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO adherence_logs (medication_id, user_id, date, status, taken_at)
            VALUES (?, ?, ?, ?, ?)
            """, (med_id, user_id, today_str, "taken", datetime.now()))

        # Seed a missed medication to showcase alert feature
        cursor.execute("""
        INSERT INTO medications (user_id, name, dosage, frequency, scheduled_time, instructions, condition_target)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, "Omega-3 Fish Oil", "1000 mg", "Once Daily", "07:30 AM", "Take with food", "Cardiovascular Support"))
        missed_med_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO adherence_logs (medication_id, user_id, date, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (missed_med_id, user_id, today_str, "missed", "Patient forgot during morning commute"))

    # Seed Pharmacy Catalog if empty
    # Seed or Update Pharmacy Catalog with Indian Rupees (₹)
    cursor.execute("DELETE FROM pharmacy_medicines")
    medicines = [
        # Fever, Pain & Headaches
        ("Paracetamol Dolo 650", "650 mg", "Fever & Pain Relief", "Tablets (Strip of 15)", 32.00, 42.00, "In Stock", "Fast relief for high fever (>100°F), headaches and body aches. Timing: Morning, Afternoon, Night after meals.", 0),
        ("Paracetamol Calpol 500", "500 mg", "Fever & Pain Relief", "Tablets (Strip of 15)", 25.00, 32.00, "In Stock", "Standard antipyretic for mild-to-moderate fever. Timing: Every 6-8 hours after food.", 0),
        ("Brufen 400 (Ibuprofen)", "400 mg", "Fever & Pain Relief", "Tablets (Strip of 15)", 28.00, 36.00, "In Stock", "Non-steroidal anti-inflammatory for joint, muscle pain and fever. Timing: After meals with water.", 0),
        ("Combiflam (Ibuprofen + Paracetamol)", "400mg/325mg", "Fever & Pain Relief", "Tablets (Strip of 20)", 42.00, 52.00, "In Stock", "Combined pain and acute inflammation relief. Timing: Afternoon and Night after meals.", 0),
        ("Meftal-Spas (Mefenamic Acid + Dicyclomine)", "250mg/10mg", "Fever & Pain Relief", "Tablets (Strip of 10)", 48.00, 60.00, "In Stock", "Relieves spasmodic stomach colic, cramps and acute abdominal pain. Timing: As needed after meals.", 1),
        ("Saridon Triple Action", "250mg/150mg/50mg", "Fever & Pain Relief", "Tablets (Strip of 10)", 45.00, 54.00, "In Stock", "Quick-acting headache and migraine relief. Timing: Once as needed after food.", 0),

        # Antibiotics & Anti-Infectives (Rx)
        ("Augmentin 625 Duo (Amoxicillin + Clavulanate)", "625 mg", "Antibiotics & Infections", "Tablets (Strip of 10)", 185.00, 220.00, "In Stock", "Broad-spectrum antibacterial for throat, lung, skin, and urinary infections. Timing: Morning & Night at start of meal.", 1),
        ("Azithral 500 (Azithromycin)", "500 mg", "Antibiotics & Infections", "Tablets (Strip of 5)", 120.00, 145.00, "In Stock", "Macrolide antibiotic for respiratory tract and bronchial infections. Timing: Morning 1 hour before or 2 hours after meals.", 1),
        ("Taxim-O 200 (Cefixime)", "200 mg", "Antibiotics & Infections", "Tablets (Strip of 10)", 110.00, 135.00, "In Stock", "Potent cephalosporin antibiotic for typhoid, ear, and respiratory infections. Timing: Morning & Night after meals.", 1),
        ("Ciplox 500 (Ciprofloxacin)", "500 mg", "Antibiotics & Infections", "Tablets (Strip of 10)", 45.00, 58.00, "In Stock", "Fluoroquinolone antibiotic for gastrointestinal and urinary tract infections. Timing: Twice daily with water.", 1),
        ("Flagyl 400 (Metronidazole)", "400 mg", "Antibiotics & Infections", "Tablets (Strip of 15)", 24.00, 32.00, "In Stock", "Antimicrobial for amoebic diarrhea, dental, and anaerobic gut infections. Timing: Morning, Afternoon, Night after meals.", 1),

        # Antivirals, Flu, Cough & Allergy
        ("Tamiflu / Antiflu (Oseltamivir)", "75 mg", "Antivirals & Cold / Flu", "Capsules (Strip of 10)", 480.00, 560.00, "In Stock", "Targeted antiviral against Influenza A & B viral pathogens. Timing: Morning & Night after meals for 5 days.", 1),
        ("Cetzine 10 (Cetirizine)", "10 mg", "Antivirals & Cold / Flu", "Tablets (Strip of 10)", 22.00, 28.00, "In Stock", "Fast non-drowsy relief for running nose, allergic sneezing and watery eyes. Timing: Night after dinner.", 0),
        ("Monticope / Telekast-L (Levocetirizine + Montelukast)", "5mg/10mg", "Antivirals & Cold / Flu", "Tablets (Strip of 10)", 95.00, 120.00, "In Stock", "Dual action for allergic rhinitis, viral airway irritation and nighttime cough. Timing: Once daily at bedtime.", 1),
        ("Ascoril-D Plus Cough Syrup", "100 ml", "Antivirals & Cold / Flu", "Syrup Bottle (100 ml)", 115.00, 138.00, "In Stock", "Sugar-free soothing syrup for dry, hacking cough and throat irritation. Timing: 10ml Morning & Night after meals.", 0),
        ("Benadryl Cough Formula", "100 ml", "Antivirals & Cold / Flu", "Syrup Bottle (100 ml)", 125.00, 150.00, "In Stock", "Expectorant relief for chesty cough, phlegm and bronchial congestion. Timing: 10ml Three times daily after food.", 0),
        ("Otrivin Adult Nasal Spray", "10 ml", "Antivirals & Cold / Flu", "Spray Bottle (10 ml)", 98.00, 115.00, "In Stock", "Fast 25-second relief for blocked nose and sinus congestion. Timing: 1 spray per nostril Morning & Night.", 0),

        # Diabetes & Metabolic
        ("Metformin Glycomet", "500 mg", "Diabetes & Metabolic", "Tablets (Strip of 10)", 68.00, 85.00, "In Stock", "First-line blood glucose regulator; increases cellular insulin sensitivity. Timing: Morning & Night after meals.", 1),
        ("Glycomet-GP 1 (Metformin + Glimepiride)", "500mg/1mg", "Diabetes & Metabolic", "Tablets (Strip of 10)", 92.00, 115.00, "In Stock", "Dual therapy for Type 2 diabetes when single agent is insufficient. Timing: Morning 15 mins before breakfast.", 1),
        ("Amaryl 2mg (Glimepiride)", "2 mg", "Diabetes & Metabolic", "Tablets (Strip of 15)", 110.00, 135.00, "In Stock", "Sulfonylurea stimulating pancreatic insulin release. Timing: Once daily Morning before breakfast.", 1),
        ("Forxiga 10mg (Dapagliflozin)", "10 mg", "Diabetes & Metabolic", "Tablets (Strip of 14)", 620.00, 720.00, "In Stock", "SGLT2 inhibitor expelling excess glucose via kidneys; protects heart and kidneys. Timing: Morning with water.", 1),
        ("Galvus 50mg (Vildagliptin)", "50 mg", "Diabetes & Metabolic", "Tablets (Strip of 14)", 245.00, 290.00, "In Stock", "DPP-4 inhibitor stabilizing post-prandial glycemic spikes. Timing: Morning & Night before or after food.", 1),

        # Blood Pressure & Heart Care
        ("Telma 40 (Telmisartan)", "40 mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 85.00, 105.00, "In Stock", "ARB antihypertensive for essential hypertension and cardiac protection. Timing: Once daily Morning after breakfast.", 1),
        ("Telma-AM (Telmisartan 40mg + Amlodipine 5mg)", "40mg/5mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 128.00, 155.00, "In Stock", "Synergistic dual therapy for uncontrolled high blood pressure. Timing: Once daily Morning after food.", 1),
        ("Amlong 5 (Amlodipine)", "5 mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 48.00, 60.00, "In Stock", "Calcium channel blocker dilating coronary and peripheral blood vessels. Timing: Once daily Morning after breakfast.", 1),
        ("Atorva 10 (Atorvastatin)", "10 mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 95.00, 118.00, "In Stock", "Lowers LDL cholesterol and stabilizes coronary arterial plaque. Timing: Once daily Night after dinner.", 1),
        ("Atorva 20 (Atorvastatin)", "20 mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 145.00, 175.00, "In Stock", "Intensive lipid lowering for high cardiac risk and post-stent care. Timing: Once daily Night at bedtime.", 1),
        ("Ecosprin 75 (Aspirin)", "75 mg", "Blood Pressure & Heart", "Tablets (Strip of 14)", 18.00, 24.00, "In Stock", "Low-dose antiplatelet preventing heart attack and ischemic stroke blood clots. Timing: Once daily Afternoon after lunch.", 1),
        ("Clopilet 75 (Clopidogrel)", "75 mg", "Blood Pressure & Heart", "Tablets (Strip of 15)", 78.00, 95.00, "In Stock", "Platelet aggregation inhibitor for acute coronary syndrome. Timing: Once daily with food.", 1),

        # Acidity, Digestion & Stomach Care
        ("Pan 40 (Pantoprazole)", "40 mg", "Acidity & Stomach Care", "Tablets (Strip of 15)", 95.00, 118.00, "In Stock", "Proton pump inhibitor healing acid reflux, heartburn and peptic ulcers. Timing: Morning 30 mins before breakfast.", 1),
        ("Pan-D (Pantoprazole + Domperidone)", "40mg/30mg", "Acidity & Stomach Care", "Capsules (Strip of 15)", 145.00, 178.00, "In Stock", "Relieves gastroesophageal reflux with nausea, belching and gas fullness. Timing: Morning 30 mins before breakfast.", 1),
        ("Omez 20 (Omeprazole)", "20 mg", "Acidity & Stomach Care", "Capsules (Strip of 15)", 58.00, 72.00, "In Stock", "Rapid relief for sour stomach, gastritis, and hyperacidity. Timing: Morning on empty stomach.", 0),
        ("Digene Antacid Gel (Mint)", "200 ml", "Acidity & Stomach Care", "Liquid Bottle (200 ml)", 140.00, 165.00, "In Stock", "Fast neutralizer for burning heartburn, acidity and gas bubbles. Timing: 10ml Afternoon & Night after meals.", 0),
        ("Electral ORS Powder (Oral Rehydration Salts)", "21.8 g", "Acidity & Stomach Care", "Sachets (Box of 5)", 38.00, 48.00, "In Stock", "WHO-recommended oral rehydration salts for dehydration, vomiting and diarrhea. Timing: Dissolve in 1 liter clean water and sip throughout day.", 0),
        ("Imodium 2mg (Loperamide)", "2 mg", "Acidity & Stomach Care", "Capsules (Strip of 10)", 35.00, 44.00, "In Stock", "Rapid motility reducer for acute watery diarrhea and loose motions. Timing: Take 1 capsule after loose stool.", 0),
        ("Cremaffin Plus Laxative Syrup", "225 ml", "Acidity & Stomach Care", "Syrup Bottle (225 ml)", 165.00, 195.00, "In Stock", "Gentle overnight constipation relief with liquid paraffin and milk of magnesia. Timing: 15ml Night before sleep.", 0),

        # Anemia, Vitamins & Immunity
        ("Orofer-XT (Ferrous Ascorbate + Folic Acid)", "100mg/1.5mg", "Vitamins & Immunity", "Tablets (Strip of 10)", 175.00, 210.00, "In Stock", "Replenishes depleted red blood cells and cures iron deficiency anemia. Timing: Night 1 hour after dinner with water.", 1),
        ("Autrin Iron & B12", "100 mg", "Vitamins & Immunity", "Capsules (Strip of 30)", 145.00, 175.00, "In Stock", "Comprehensive hematinic formula with Iron, Vitamin B12 and Folate. Timing: Once daily after meals.", 0),
        ("Becosules Z (B-Complex + Zinc)", "50 mg", "Vitamins & Immunity", "Capsules (Strip of 20)", 48.00, 58.00, "In Stock", "Replenishes essential B-vitamins, heals mouth ulcers and boosts stamina. Timing: Once daily Morning after breakfast.", 0),
        ("Calcirol 60,000 IU (Vitamin D3)", "60,000 IU", "Vitamins & Immunity", "Capsules (Pack of 4)", 85.00, 105.00, "In Stock", "Weekly high-strength bone strengthener, calcium absorption and immune booster. Timing: Once weekly after meal with milk.", 0),
        ("Limcee 500 (Vitamin C Chewable)", "500 mg", "Vitamins & Immunity", "Tablets (Strip of 15)", 30.00, 38.00, "In Stock", "Antioxidant and immunity booster; promotes wound healing and iron absorption. Timing: Once daily Morning chewable.", 0),
        ("Neurobion Forte (B1 + B6 + B12)", "100mg/100mg/200mcg", "Vitamins & Immunity", "Tablets (Strip of 30)", 38.00, 46.00, "In Stock", "Nerve regeneration, diabetic tingling/numbness and muscle weakness therapy. Timing: Once daily after lunch.", 0),
        ("Shelcal 500 (Calcium + D3)", "500mg/250IU", "Vitamins & Immunity", "Tablets (Strip of 15)", 125.00, 150.00, "In Stock", "Bioavailable calcium for osteopenia, joint health and menopausal bone loss. Timing: Afternoon after lunch.", 0),

        # Respiratory & Inhalers
        ("Asthalin 100 mcg Inhaler (Salbutamol)", "100 mcg", "Respiratory & Asthma", "Inhaler Canister (200 Doses)", 145.00, 175.00, "In Stock", "Fast-acting bronchodilator for acute asthma attack, wheezing and dyspnea. Timing: 1-2 puffs SOS or Morning & Night.", 1),
        ("Budecort 200 Inhaler (Budesonide)", "200 mcg", "Respiratory & Asthma", "Inhaler Canister (200 Doses)", 280.00, 335.00, "In Stock", "Inhaled steroid preventing chronic airway inflammation and bronchial edema. Timing: 1 puff Morning & Night after meals.", 1),
        ("Foracort 200 Inhaler (Budesonide + Formoterol)", "200mcg/6mcg", "Respiratory & Asthma", "Inhaler Canister (200 Doses)", 395.00, 465.00, "In Stock", "Combination steroid and long-acting bronchodilator for moderate-severe asthma/COPD. Timing: 1 puff Morning & Night.", 1),
        ("Karvol Plus Inhalation Capsules", "250 mg", "Respiratory & Asthma", "Softgels (Pack of 10)", 85.00, 105.00, "In Stock", "Aromatic decongestant capsule for steam inhalation during severe flu and sinus blockage. Timing: Pierce into hot water Night before sleep.", 0),

        # Medical Devices & Test Kits
        ("Accu-Chek Active Glucose Meter & 50 Strips", "1 Kit", "Medical Diagnostic Device", "Device Kit (1 Unit + 50 Strips)", 890.00, 1050.00, "In Stock", "Capillary blood glucose self-monitoring glucometer with 5-second test time. Timing: Fasting morning & 2 hours post-meal.", 0),
        ("Accu-Chek Active Test Strips (Pack of 50)", "50 Strips", "Medical Diagnostic Device", "Device Pack (50 Strips)", 680.00, 790.00, "In Stock", "Original certified test strips for Accu-Chek Active glucometer.", 0),
        ("Omron Digital Automatic BP Monitor", "Upper Arm", "Medical Diagnostic Device", "Medical Device (1 Unit)", 1650.00, 1950.00, "In Stock", "IntelliSense technology automatic one-touch blood pressure and pulse monitor. Timing: Morning before breakfast and Night.", 0),
        ("Fingertip Pulse Oximeter Digital SpO2", "Fingertip", "Medical Diagnostic Device", "Medical Device (1 Unit)", 550.00, 750.00, "In Stock", "Precision pulse rate and oxygen saturation (SpO2) fingertip monitor with OLED screen.", 0),
        ("Digital Clinical Thermometer", "Oral/Underarm", "Medical Diagnostic Device", "Medical Device (1 Unit)", 150.00, 195.00, "In Stock", "Fast 10-second high precision fever thermometer with fever alarm beep.", 0),
        ("3-in-1 Steam Vaporizer Inhaler", "Electric", "Medical Diagnostic Device", "Device (1 Unit)", 260.00, 320.00, "In Stock", "Medical-grade steam inhaler for cough, cold, nasal decongestion and facial steaming.", 0)
    ]
    for m in medicines:
        cursor.execute("""
        INSERT INTO pharmacy_medicines (name, strength, category, form, price, discount_price, stock_status, description, rx_required)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, m)

    # Seed or Update Live Nearby Hospitals Directory with authentic prominent hospitals
    cursor.execute("DELETE FROM hospitals_directory")
    hospitals = [
        # Ananthapuramu / Anantapur
        ("Government General Hospital (GGH / RIMS)", "Emergency & Trauma / Multi-Speciality", 0.8, "Subhash Road, Opp. District Collectorate", "Ananthapuramu", "+91 8554-275155", 8, 32, 220, 4.6, 1, 14.6819, 77.6006),
        ("Saveera Multi Speciality Hospital", "Multi-Speciality & Critical Care", 1.4, "D.No 1-135, R.F. Road, Near Clock Tower", "Ananthapuramu", "+91 8554-245555", 10, 24, 90, 4.8, 1, 14.6760, 77.5930),
        ("KIMS-Saveera Super Speciality Hospital", "Cardiology & Emergency Care", 2.2, "NH 44, Bengaluru-Hyderabad Highway", "Ananthapuramu", "+91 8554-297777", 12, 20, 110, 4.7, 1, 14.6920, 77.6150),
        
        # Bengaluru / Bangalore
        ("Manipal Hospital, Old Airport Road", "Multi-Speciality & Quaternary Care", 2.1, "98 HAL Old Airport Rd, Kodihalli", "Bengaluru", "+91 80-25024444", 6, 45, 280, 4.9, 1, 12.9584, 77.6508),
        ("Apollo Hospitals, Bannerghatta Road", "Multi-Speciality & Emergency Trauma", 3.2, "154/11 Opp. IIMB, Bannerghatta Main Rd", "Bengaluru", "+91 80-26304050", 9, 38, 250, 4.8, 1, 12.8938, 77.5979),
        ("Narayana Institute of Cardiac Sciences", "Cardiac Surgery & Super Speciality", 4.5, "258/A Bommasandra Industrial Area, Anekal Taluk", "Bengaluru", "+91 80-71222222", 7, 50, 310, 4.9, 1, 12.8124, 77.6895),
        ("Fortis Hospital, Cunningham Road", "Cardiology & Critical Care", 3.8, "14 Cunningham Rd, Vasanth Nagar", "Bengaluru", "+91 80-41994444", 10, 26, 150, 4.8, 1, 12.9863, 77.5940),

        # Hyderabad
        ("Apollo Health City, Jubilee Hills", "Multi-Specialty & Organ Transplant", 2.8, "Road No 72, Film Nagar, Jubilee Hills", "Hyderabad", "+91 40-23607777", 8, 42, 290, 4.9, 1, 17.4156, 78.4124),
        ("KIMS Hospitals (Krishna Institute of Medical Sciences)", "Multi-Speciality & Emergency Care", 3.6, "1-8-31/1 Minister Road, Begumpet", "Hyderabad", "+91 40-44885000", 11, 36, 260, 4.8, 1, 17.4375, 78.4867),
        ("Care Hospitals, Banjara Hills", "Cardiology & Critical Care", 4.1, "Road No. 1 Prem Nagar, Banjara Hills", "Hyderabad", "+91 40-61656565", 10, 28, 180, 4.7, 1, 17.4168, 78.4483),
        ("Yashoda Hospitals, Somajiguda", "Multi-Speciality & Neuro Sciences", 3.4, "Raj Bhavan Rd, Somajiguda", "Hyderabad", "+91 40-45674567", 9, 34, 240, 4.8, 1, 17.4258, 78.4589),

        # New Delhi / NCR
        ("AIIMS (All India Institute of Medical Sciences)", "Apex Emergency & Super Speciality", 1.8, "Sri Aurobindo Marg, Ansari Nagar East", "New Delhi", "+91 11-26588500", 12, 65, 450, 4.9, 1, 28.5672, 77.2100),
        ("Fortis Memorial Research Institute (FMRI)", "Oncology & Multi-Speciality", 3.9, "Sector 44, Opp. HUDA City Centre Metro", "New Delhi", "+91 124-4962200", 14, 30, 210, 4.8, 1, 28.4595, 77.0725),
        ("Max Super Speciality Hospital, Saket", "Cardiac & Multi-Speciality", 2.6, "1, 2 Press Enclave Marg, Saket", "New Delhi", "+91 11-26515050", 8, 40, 280, 4.9, 1, 28.5284, 77.2114),

        # Chennai
        ("Apollo Hospitals, Greams Road", "Multi-Speciality & Cardiac Excellence", 2.4, "21 Greams Lane, Thousand Lights", "Chennai", "+91 44-28290200", 7, 40, 320, 4.9, 1, 13.0604, 80.2524),
        ("MGM Healthcare", "Cardiac & Quaternary Care", 3.1, "72 Nelson Manickam Rd, Aminjikarai", "Chennai", "+91 44-45242424", 9, 32, 220, 4.8, 1, 13.0734, 80.2185),

        # Vellore
        ("Christian Medical College (CMC)", "Multi-Speciality & Tertiary Care", 5.2, "Ida Scudder Road", "Vellore", "+91 416-2281000", 15, 48, 380, 4.9, 1, 12.9254, 79.1356),

        # Visakhapatnam / Vizag
        ("Apollo Health City, Arilova", "Multi-Speciality & Cancer Institute", 3.5, "Chinagadili, Arilova", "Visakhapatnam", "+91 891-2867777", 10, 30, 200, 4.8, 1, 17.7554, 83.3324),
        ("King George Hospital (GGH / KGH)", "Government Apex Emergency", 1.5, "Maharanipeta", "Visakhapatnam", "+91 891-2564891", 8, 38, 350, 4.5, 1, 17.7084, 83.3056),

        # Vijayawada
        ("Manipal Hospital, Tadepalli", "Multi-Speciality & Critical Care", 2.8, "Near Kanaka Durga Varadhi, Tadepalli", "Vijayawada", "+91 866-2495555", 9, 28, 190, 4.8, 1, 16.4883, 80.6200),
        ("Ramesh Hospitals, Ring Road", "Cardiology & Emergency Trauma", 3.2, "Near ITI Road, Ring Road", "Vijayawada", "+91 866-2488888", 7, 32, 210, 4.8, 1, 16.5062, 80.6480),

        # Tirupati
        ("Sri Venkateswara Institute of Medical Sciences (SVIMS)", "Apex Super Speciality & Cardiac", 2.0, "Alipiri Road", "Tirupati", "+91 877-2287777", 11, 40, 300, 4.7, 1, 13.6373, 79.4064),
        ("SVRR Government General Hospital (Ruia)", "Emergency Trauma Care", 1.2, "Alipiri Bypass Road", "Tirupati", "+91 877-2286666", 8, 30, 250, 4.6, 1, 13.6335, 79.4125),

        # Kurnool
        ("Government General Hospital (GGH Kurnool)", "Government Emergency & Trauma", 1.1, "Budhawara Peta", "Kurnool", "+91 8518-255155", 9, 35, 280, 4.5, 1, 15.8281, 78.0373),
        ("KIMS Hospitals, Kurnool", "Multi-Speciality & Cardiac Center", 2.4, "Joharapuram Road", "Kurnool", "+91 8518-297777", 10, 22, 120, 4.7, 1, 15.8152, 78.0465),

        # Mumbai
        ("Tata Memorial Hospital", "Apex Oncology & Emergency", 3.0, "Dr. E Borges Road, Parel", "Mumbai", "+91 22-24177000", 12, 50, 400, 4.9, 1, 19.0044, 72.8427),
        ("Kokilaben Dhirubhai Ambani Hospital", "Multi-Speciality & Quaternary Care", 4.2, "Rao Saheb Achutrao Patwardhan Marg, Andheri West", "Mumbai", "+91 22-30696969", 8, 48, 320, 4.9, 1, 19.1314, 72.8252),

        # Pune
        ("Ruby Hall Clinic", "Cardiology & Multi-Speciality", 2.5, "40 Sassoon Road, Sangamvadi", "Pune", "+91 20-66455100", 9, 36, 260, 4.8, 1, 18.5308, 73.8770)
    ]
    for h in hospitals:
        cursor.execute("""
        INSERT INTO hospitals_directory (name, category, distance_km, address, city, phone, emergency_wait_mins, icu_beds, general_beds, rating, is_open_24_7, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, h)

    conn.commit()


def get_setting(key, default=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return default


def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO system_settings (setting_key, setting_value, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value, updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    conn.commit()
    conn.close()
