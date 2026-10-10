# Dr. AI Medicare Platform 🩺

An AI-powered Clinical Decision Support & Patient Care Platform designed to combat early chronic disease neglect, improve medication adherence, and eliminate hospital waiting room bottlenecks.

---

## 🌟 Key Features & Problem Solvers

### 1. Chronic Disease Risk & Virus Estimator + Report Analyzer (with PDF Export)
- **Problem:** Many patients ignore early warning signs of chronic conditions (Type 2 Diabetes, Hypertension, Coronary Artery Disease, Anemia, Respiratory Disorders) and rush to overcrowded hospitals only after severe escalation.
- **AI Solution:** 
  - Collects multi-select symptoms, lifestyle details (smoking, activity, sleep), biometric vitals (Blood Pressure, Fasting Glucose, SpO2, Heart Rate, BMI, Hemoglobin), and medical history.
  - Supports direct drag-and-drop file upload of medical lab reports (`.pdf`, `.txt`, `.png`, `.jpg`).
  - Reads and extracts clinical text and computes risk stratification (**Low, Moderate, High, Urgent**).
  - Connects to **Google AI Studio (Gemini 2.5 Flash / 1.5 Flash)** with structured clinical reasoning, or runs on an integrated evidence-based **Clinical Heuristic Engine** (AHA/ADA/WHO criteria) when offline.
  - Automatically compiles and generates a downloadable, official **Clinical Medical Summary Report (PDF)** built via ReportLab.
  - **Important Clinical Disclaimer:** Designed solely to assist clinicians and patients; does *not* replace licensed physician diagnosis.

### 2. Medicine Reminder & Adherence Tracker
- **Problem:** Elderly patients and people with chronic illnesses frequently miss doses, take wrong strengths, or terminate therapy prematurely.
- **AI Solution:**
  - Real-time prescription schedule with daily time slots, dosage, and target condition.
  - Interactive "Take Dose" and "Mark Missed" controls.
  - Dynamic **Adherence Score Ring Gauge** (percentage calculation).
  - **Caregiver Alert Dispatcher:** Automatically detects repeated missed doses and simulates/sends an urgent alert to the designated caregiver (e.g., family member or nurse) via SMS/Email.
  - Web Audio API synthesizer for reminder chime audio cues.

### 3. Hospital Queue & Appointment Wait Time Prediction
- **Problem:** Patients wait hours at hospitals without knowing doctor availability, consultation speed, or queue depth.
- **AI Solution:**
  - AI wait time prediction formula: `(Patients Ahead × Avg Consult Mins) + Rush Hour Buffer + Emergency Triage Factor`.
  - Live Digital Token Display (`Currently Serving`, `Your Token`, `Patients Ahead`, `Estimated Wait Mins`).
  - Interactive **Queue Advance Simulator** allows users to watch the live queue move forward and dynamically recalculate waiting time.
  - Multi-department directory (Cardiology, Endocrinology, Pulmonology, General OPD) with instant token generation.

---

## 🎨 UI Design Specification
- **Clean White Background:** Crisp, high-contrast healthcare theme (`#ffffff` base with soft slate borders and teal/cyan medical accents).
- **Doctor's Logo in the Middle:** Prominent, centered medical branding featuring a doctor avatar, stethoscope, caduceus cross, and animated pulse wave.
- **Workable Interactive Buttons:** Every button, tab, modal, preset loader, file upload, audio chime, and queue advancement control is fully functional.

---

## 🛠️ Technology Stack
- **Backend:** Python (Flask, ReportLab, PyPDF, Requests, SQLite3)
- **Database:** SQLite (`medicare.db`) storing users, health records, medications, adherence logs, queue tickets, and AI settings.
- **AI Engine:** Google AI Studio (Gemini 2.5 Flash / 1.5 Flash) via REST API with automated fallback to the clinical heuristic engine.
- **PDF Engine:** ReportLab Platypus generating high-resolution clinical documents.
- **Frontend:** Vanilla JavaScript (ES6+), Web Audio API, responsive modern CSS.

---

## 🚀 Quick Start Guide

### 1. Requirements
Ensure Python is installed:
```powershell
py --version
```

### 2. Install Dependencies
```powershell
cd C:\Users\prith\.gemini\antigravity\scratch\healthpulse-ai
py -m pip install -r requirements.txt
```

### 3. Configure Google AI Studio Gemini API Key (Optional)
You can configure your key in two ways:
1. **Via the Web Interface (Recommended):** Click the **"🔑 AI Studio: Connect"** button in the header, paste your key, click **Verify Connection**, then **Save & Activate Key**.
2. **Via `.env` file or environment variable:**
   ```powershell
   $env:GEMINI_API_KEY="your-google-ai-studio-key"
   ```

*Note: If no API key is provided, the platform automatically runs on its built-in clinical expert engine so you can test all features immediately!*

### 4. Run the Server
```powershell
py app.py
```
Open your browser at:
👉 **`http://127.0.0.1:5000`**

### 5. Run the Automated Test Suite
```powershell
py test_app.py
```

---

## 🌐 Deploy to Render (Free Cloud Hosting)

Dr. AI Medicare is fully pre-configured for free deployment on **Render**:

### Step 1: Push Project to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Dr. AI Medicare production release"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 2: Create Web Service on Render
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Render automatically reads the configuration. Verify these settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. *(Optional)* In **Environment Variables**, add:
   - `SECRET_KEY`: (any secure random string)
   - `GEMINI_API_KEY`: (your Google AI Studio key, or leave blank to use the offline heuristic engine)
   - `GOOGLE_CLIENT_ID`: (your Google OAuth client ID, if configured)
6. Click **Deploy Web Service**.

Your live URL will be provisioned (e.g., `https://dr-ai-medicare.onrender.com`).

---

## 📂 Project Structure
```
healthpulse-ai/
│
├── app.py                  # Flask application entry point & REST API endpoints
├── database.py             # SQLite schema, auto-initialization, & seed data
├── gemini_service.py       # Google AI Studio Gemini connector & clinical logic
├── pdf_generator.py        # ReportLab clinical PDF summary generator
├── Procfile                # Production process declaration for Render (gunicorn app:app)
├── render.yaml             # Render Blueprint specification for 1-click cloud deploy
├── requirements.txt        # Production Python dependencies (Flask, Gunicorn, ReportLab)
├── .gitignore              # Excludes secrets, databases, caches, and patient uploads
├── .env.example            # Environment variables template
├── README.md               # Complete platform documentation & setup guide
│
├── templates/
│   └── index.html          # Main web application (Doctor logo center & white theme)
│
├── static/
│   ├── css/
│   │   └── style.css       # Clean white healthcare stylesheet & responsive grid
│   ├── js/
│   │   └── app.js          # Client-side controller for tabs, modals, & APIs
│   └── images/
│       ├── dr-pruthve-logo.svg # Central doctor emblem & pulse wave graphic
│       └── google-logo.svg     # Google identity logo
│
└── uploads/
    ├── sample_reports/     # Pre-built sample clinical test reports (PDF)
    └── reports/            # Generated clinical PDF reports & patient uploads
```

