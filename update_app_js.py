# update_app_js.py
import json
import re

with open("translations_generated.json", "r", encoding="utf-8") as f:
    translations_data = json.load(f)

with open("static/js/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 1. Prepare JS string for TRANSLATIONS
translations_js = "const TRANSLATIONS = " + json.dumps(translations_data, ensure_ascii=False, indent=2) + ";\n"

# Replace TRANSLATIONS object in app.js
# From 'const TRANSLATIONS = {' up to 'const voiceAdvisorTexts = {'
translations_pattern = re.compile(r"const TRANSLATIONS\s*=\s*\{.*?\n\};\n\nconst voiceAdvisorTexts", re.DOTALL)
if translations_pattern.search(app_js):
    app_js = translations_pattern.sub(translations_js + "\nconst voiceAdvisorTexts", app_js)
    print("Replaced TRANSLATIONS successfully.")
else:
    print("WARNING: Could not find TRANSLATIONS pattern directly, attempting alternative match.")

# 2. Prepare comprehensive applyLanguage(lang)
apply_language_code = """function applyLanguage(lang) {
  currentLanguage = lang;
  const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
  
  const setTxt = (sel, val) => {
    if (!val) return;
    const el = document.querySelector(sel);
    if (el) el.textContent = val;
  };

  const setHtml = (sel, val) => {
    if (!val) return;
    const el = document.querySelector(sel);
    if (el) el.innerHTML = val;
  };

  const setAttr = (sel, attr, val) => {
    if (!val) return;
    const el = document.querySelector(sel);
    if (el) el.setAttribute(attr, val);
  };

  // --- Header & Announcements ---
  setTxt(".top-announcement span", t.banner_text);
  setTxt(".header-left .who-badge div div:first-child", t.care_network_title);
  setTxt(".header-left .who-badge div div:last-child", t.global_protocols);
  setTxt(".brand-subtitle", t.brand_subtitle);
  setTxt("#google-login-btn-text", t.google_signin_btn);
  setTxt("#btn-google-signout", t.sign_out);
  setTxt("#gemini-status-indicator", t.gemini_key_btn);

  // --- Header Module Boxes (Tabs) ---
  setTxt("#header-box-analyzer .module-box-title", t.tab_analyzer_title);
  setTxt("#header-box-analyzer .module-box-pill", t.tab_analyzer_pill);
  setTxt("#header-box-analyzer .module-box-desc", t.tab_analyzer_desc);

  setTxt("#header-box-meds .module-box-title", t.tab_meds_title);
  setTxt("#header-box-meds .module-box-pill", t.tab_meds_pill);
  setTxt("#header-box-meds .module-box-desc", t.tab_meds_desc);

  setTxt("#header-box-hospitals .module-box-title", t.tab_hospitals_title);
  setTxt("#header-box-hospitals .module-box-pill", t.tab_hospitals_pill);
  setTxt("#header-box-hospitals .module-box-desc", t.tab_hospitals_desc);

  setTxt("#header-box-profile .module-box-title", t.tab_profile_title);
  setTxt("#header-box-profile .module-box-pill", t.tab_profile_pill);
  setTxt("#header-box-profile .module-box-desc", t.tab_profile_desc);

  // --- Hero Section ---
  setHtml(".hero-title", t.hero_welcome);
  setTxt(".hero-desc", t.hero_desc);
  
  const pills = document.querySelectorAll(".hero-highlights .highlight-pill");
  if (pills.length >= 4) {
    const updatePill = (el, txt) => {
      const svg = el.querySelector("svg");
      el.innerHTML = "";
      if (svg) el.appendChild(svg);
      el.appendChild(document.createTextNode(" " + txt));
    };
    updatePill(pills[0], t.hero_pill_1);
    updatePill(pills[1], t.hero_pill_2);
    updatePill(pills[2], t.hero_pill_3);
    updatePill(pills[3], t.hero_pill_4);
  }

  // --- Voice Advisor Card ---
  setTxt(".voice-advisor-card .card-title", t.voice_card_title);
  setTxt(".voice-advisor-card .card-subtitle", t.voice_card_sub);
  setTxt("#btn-play-voice-advisor span", t.btn_listen);
  setTxt("#btn-pause-voice-advisor span", t.btn_pause);
  setTxt("#btn-stop-voice-advisor span", t.btn_stop);

  const voiceLangCard = document.getElementById("select-voice-language-card");
  if (voiceLangCard && voiceLangCard.value !== lang) {
    voiceLangCard.value = lang;
  }

  const topicSelect = document.getElementById("select-voice-topic");
  if (topicSelect) {
    const optWelcome = topicSelect.querySelector('option[value="welcome"]');
    if (optWelcome) optWelcome.textContent = t.topic_welcome;
    const optChronic = topicSelect.querySelector('option[value="chronic"]');
    if (optChronic) optChronic.textContent = t.topic_chronic;
    const optMed = topicSelect.querySelector('option[value="medication"]');
    if (optMed) optMed.textContent = t.topic_medication;
    const optRep = topicSelect.querySelector('option[value="report"]');
    if (optRep) optRep.textContent = t.topic_report;
    const optEmerg = topicSelect.querySelector('option[value="emergency"]');
    if (optEmerg) optEmerg.textContent = t.topic_emergency;
  }

  const transcriptEl = document.getElementById("voice-transcript-display");
  const topic = topicSelect ? topicSelect.value : "welcome";
  const texts = voiceAdvisorTexts[lang] || voiceAdvisorTexts.en;
  if (transcriptEl) {
    transcriptEl.textContent = texts[topic] || texts.welcome;
  }

  // --- Tab 1: Dropzone & Sample Reports ---
  setTxt("#tab-analyzer .grid-2col > div:first-child .card-header .card-title", t.dropzone_card_title);
  setTxt("#tab-analyzer .grid-2col > div:first-child .card-header .card-subtitle", t.dropzone_card_sub);
  setTxt(".dropzone-main-text", t.dropzone_main_text);
  setTxt(".dropzone-sub-text", t.dropzone_sub_text);
  setTxt("#btn-browse-pdf", t.btn_browse_pdf);
  setTxt("#pdf-uploading-spinner strong", t.spinner_reading);

  setTxt("#btn-sample-diabetic .sample-pdf-title span", t.sample_diabetic_title);
  setTxt("#btn-sample-diabetic .sample-pdf-desc", t.sample_diabetic_desc);
  setTxt("#btn-sample-viral .sample-pdf-title span", t.sample_viral_title);
  setTxt("#btn-sample-viral .sample-pdf-desc", t.sample_viral_desc);
  setTxt("#btn-sample-anemia .sample-pdf-title span", t.sample_anemia_title);
  setTxt("#btn-sample-anemia .sample-pdf-desc", t.sample_anemia_desc);
  document.querySelectorAll(".sample-pdf-card .text-xs").forEach(el => {
    el.textContent = t.sample_run_text;
  });

  // --- Tab 1: Clinical Evaluation Results Card ---
  setTxt("#analysis-results-card .card-title", t.results_card_title);
  setTxt("#btn-download-pdf-top", t.btn_download_pdf_top);
  setTxt("#btn-download-pdf-main", t.btn_download_pdf_main);
  setTxt("#results-empty-state h4", t.awaiting_pdf_title);
  setTxt("#results-empty-state p", t.awaiting_pdf_desc);
  setTxt("#output-traffic-subtitle", t.traffic_subtitle);
  setTxt("#btn-voice-readout span", t.btn_voice_readout);
  setTxt('[data-i18n="results_conditions_title"]', t.risks_identified_title);
  setTxt('[data-i18n="results_meds_schedule_title"]', t.meds_schedule_title);
  setTxt('[data-i18n="results_meds_badge"]', t.meds_schedule_badge);
  setTxt('[data-i18n="results_meds_desc"]', t.meds_schedule_desc);

  // --- Tab 2: Medicine Reminder & Adherence ---
  setTxt("#medication-todo-container .todo-header h3", t.todo_card_title);
  setTxt("#medication-todo-container .todo-header p", t.todo_card_sub);
  setTxt("#todo-progress-text", t.doses_taken_text);
  setTxt("#btn-open-add-med-modal", t.btn_open_add_med);
  setTxt("#btn-simulate-sound-chime", t.btn_test_chime);

  setTxt('#todo-time-filters [data-time="all"]', t.filter_all_doses);
  setTxt('#todo-time-filters [data-time="Morning"]', t.filter_morning);
  setTxt('#todo-time-filters [data-time="Afternoon"]', t.filter_afternoon);
  setTxt('#todo-time-filters [data-time="Evening"]', t.filter_evening);
  setTxt('#todo-time-filters [data-time="Night"]', t.filter_night);

  setTxt("#btn-trigger-caregiver-alert", t.btn_send_caregiver_alert);

  // --- Tab 2: Online Pharmacy Store ---
  setTxt("#pharmacy-store-section .card-title", t.pharmacy_store_title);
  setTxt("#pharmacy-store-section .card-subtitle", t.pharmacy_store_sub);
  setTxt("#btn-order-active-prescriptions", t.btn_auto_order_presc);
  setAttr("#input-pharmacy-search", "placeholder", t.pharmacy_search_placeholder);

  setTxt('#pharmacy-category-filters [data-category="all"]', t.cat_all);
  setTxt('#pharmacy-category-filters [data-category="Diabetes"]', t.cat_diabetes);
  setTxt('#pharmacy-category-filters [data-category="Cardiology"]', t.cat_cardiology);
  setTxt('#pharmacy-category-filters [data-category="Antibiotics"]', t.cat_antibiotics);
  setTxt('#pharmacy-category-filters [data-category="Respiratory"]', t.cat_respiratory);
  setTxt('#pharmacy-category-filters [data-category="Medical Device"]', t.cat_devices);

  setTxt("#cart-items-list-text", t.cart_delivery_available);
  setTxt("#btn-clear-cart", t.btn_clear_cart);
  setTxt("#btn-open-checkout-modal", t.btn_proceed_delivery);
  setTxt("#pharmacy-store-section h4 span:first-child", t.orders_tracking_title);

  // --- Tab 3: Nearby Hospitals & Maps ---
  setTxt("#tab-hospitals h3", t.hospitals_top_title);
  setTxt("#tab-hospitals p", t.hospitals_top_sub);
  setTxt("#btn-detect-location span", t.btn_detect_gps);
  setTxt("#btn-quick-call-911", t.btn_emergency_hotline);
  setTxt("#google-maps-card strong", t.gmaps_card_title);
  setTxt("#google-maps-card .text-xs", t.gmaps_card_sub);
  setAttr("#input-hospital-search", "placeholder", t.hospital_search_ph);
  setTxt("#btn-search-maps span", t.btn_search_gmaps);
  setTxt("#btn-clear-hospital-search", t.btn_reset_maps);
  setTxt("#hospital-city-chips span:first-child", t.quick_cities_lbl);
  setTxt("#btn-open-external-maps", t.open_gmaps_app);

  setTxt("#digital-opd-card .card-title", t.opd_section_title);
  setTxt("#digital-opd-card .card-subtitle", t.opd_section_sub);
  setTxt("#btn-open-book-token span", t.btn_open_book_token);
  setTxt("#no-booked-token-card h4", t.no_active_token_title);
  setTxt("#no-booked-token-card p", t.no_active_token_desc);
  setTxt("#btn-empty-book-token span", t.btn_book_token_now);

  // --- Tab 4: Profile ---
  setTxt("#tab-profile .card-title", t.profile_card_title);
  setTxt("#tab-profile .card-subtitle", t.profile_card_sub);
  setTxt("#profile-edit-form button[type='submit']", t.btn_save_profile);

  // --- Footer ---
  setTxt(".footer-disclaimer", t.footer_disclaimer);

  // Update dynamic lists in target language
  updateClinicalResultsLanguage();
  if (lastAnalysisReportData && lastAnalysisReportData.analysis) {
    renderPrescribedMedications(lastAnalysisReportData.analysis.prescribed_medications || [], lastAnalysisReportData.pdf_url);
  }
  
  if (pharmacyCatalog && pharmacyCatalog.length > 0) {
    const activeBtn = document.querySelector("#pharmacy-category-filters .active-pill");
    const activeCat = activeBtn ? activeBtn.dataset.category : "all";
    const searchVal = document.getElementById("input-pharmacy-search")?.value.toLowerCase().trim() || "";
    filterAndRenderPharmacy(activeCat, searchVal);
  }

  if (hospitalsList && hospitalsList.length > 0) {
    renderHospitalsGrid(hospitalsList);
  }

  populateVoices();
}"""

# Replace applyLanguage function in app.js
apply_pattern = re.compile(r"function applyLanguage\(lang\)\s*\{.*?\n\}\n\nfunction initVoiceReader", re.DOTALL)
if apply_pattern.search(app_js):
    app_js = apply_pattern.sub(apply_language_code + "\n\nfunction initVoiceReader", app_js)
    print("Replaced applyLanguage successfully.")
else:
    print("WARNING: Could not find applyLanguage pattern directly.")

with open("static/js/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Updated app.js successfully.")
