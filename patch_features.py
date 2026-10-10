# patch_features.py - Patches prescribed medications and grid translations in static/js/app.js
import re

with open("static/js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update renderAnalysisResults to call renderPrescribedMedications
target_line = "updateClinicalResultsLanguage();"
replacement_line = """updateClinicalResultsLanguage();
  renderPrescribedMedications(analysis.prescribed_medications || [], data.pdf_url);"""

if target_line in js and "renderPrescribedMedications(analysis.prescribed_medications" not in js:
    js = js.replace(target_line, replacement_line, 1)
    print("Added renderPrescribedMedications call in renderAnalysisResults.")
else:
    print("renderPrescribedMedications already called or target not found.")

# 2. Add the prescribed medications rendering and quick buy functions right before loadReportsHistory
med_functions = """
/* -------------------------------------------------------------
   8b. Prescribed Disease/Virus Medications & Intake Schedule Renderer
   ------------------------------------------------------------- */
function renderPrescribedMedications(medications, pdfUrl) {
  const container = document.getElementById("output-medications-table-container");
  if (!container) return;

  const t = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;

  if (!medications || medications.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 14px; color: var(--text-muted); font-size: 0.88rem; background: #f8fafc; border-radius: var(--radius-sm); border: 1px dashed #cbd5e1;">
        ℹ️ ${currentLanguage === 'hi' ? 'कोई आपातकालीन दवा की आवश्यकता नहीं है। सामान्य स्वास्थ्य बनाए रखें।' : (currentLanguage === 'te' ? 'ఎలాంటి తక్షణ మందులు అవసరం లేదు. సాధారణ ఆరోగ్య జాగ్రత్తలు తీసుకోండి.' : 'No immediate pharmaceuticals required. Continue standard preventive care.')}
      </div>
    `;
    return;
  }

  const rowsHtml = medications.map((med) => {
    const timingStr = (med.timing || "").toLowerCase();
    const isMorning = timingStr.includes("morning");
    const isAfternoon = timingStr.includes("afternoon");
    const isNight = timingStr.includes("night") || timingStr.includes("bedtime");

    const mealStr = (med.meal_relation || "").toLowerCase();
    const isBeforeMeal = mealStr.includes("before") || mealStr.includes("empty stomach");

    // Timing badges with distinct high-contrast colors
    const morningBadge = `
      <span style="font-size: 0.74rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; ${isMorning ? 'background: #fef3c7; color: #92400e; border: 1.5px solid #f59e0b;' : 'background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; opacity: 0.6;'}">
        ${t.timing_morning || '☀️ Morning'}
      </span>
    `;

    const afternoonBadge = `
      <span style="font-size: 0.74rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; ${isAfternoon ? 'background: #e0f2fe; color: #075985; border: 1.5px solid #0284c7;' : 'background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; opacity: 0.6;'}">
        ${t.timing_afternoon || '🌤️ Afternoon'}
      </span>
    `;

    const nightBadge = `
      <span style="font-size: 0.74rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; ${isNight ? 'background: #ede9fe; color: #5b21b6; border: 1.5px solid #8b5cf6;' : 'background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; opacity: 0.6;'}">
        ${t.timing_night || '🌙 Night'}
      </span>
    `;

    // Meal schedule badge
    const mealBadge = isBeforeMeal 
      ? `<span style="font-size: 0.76rem; font-weight: 800; background: #fffbeb; color: #b45309; border: 1.5px solid #fcd34d; padding: 3px 10px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">
           ${t.meal_before || '🍽️ Before Meal'} (30m before food)
         </span>`
      : `<span style="font-size: 0.76rem; font-weight: 800; background: #ecfdf5; color: #065f46; border: 1.5px solid #6ee7b7; padding: 3px 10px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">
           ${t.meal_after || '🍛 After Meal'} (With / after food)
         </span>`;

    const encodedMed = encodeURIComponent(JSON.stringify(med));

    return `
      <div class="prescribed-med-card" style="background: #ffffff; border: 1.5px solid #bae6fd; border-left: 5px solid #0284c7; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <strong style="font-size: 1.05rem; color: #0c4a6e; letter-spacing: -0.2px;">
                💊 ${med.name}
              </strong>
              ${med.generic ? `<span style="font-size: 0.76rem; color: #0369a1; background: #f0f9ff; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #e0f2fe;">${med.generic}</span>` : ''}
            </div>
            <div style="font-size: 0.82rem; color: #0369a1; font-weight: 700; margin-top: 3px;">
              🎯 ${med.condition_target || 'Target Disease'}
            </div>
          </div>
          
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            ${mealBadge}
          </div>
        </div>

        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 0.78rem; font-weight: 700; color: #475569;">${t.th_timing || 'Daily Intake Timing'}:</span>
            ${morningBadge}
            ${afternoonBadge}
            ${nightBadge}
          </div>
          <div style="font-size: 0.82rem; color: #334155;">
            <strong>${med.dosage || ''}</strong> • <span style="color: #64748b;">${med.frequency || ''} • ${med.duration || ''}</span>
          </div>
        </div>

        <div style="font-size: 0.84rem; color: #475569; margin-bottom: 12px; line-height: 1.45;">
          📝 <strong>Instructions:</strong> ${med.instructions || 'Take as advised with water.'}
        </div>

        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; border-top: 1px dashed #e2e8f0; padding-top: 10px;">
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button type="button" class="btn btn-primary btn-sm" style="background: #0284c7; border-color: #0284c7; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem; padding: 6px 12px;" onclick="quickBuyPrescriptionMedicine('${med.name.replace(/'/g, "\\\\'")}', '${(med.pharmacy_match || med.name).replace(/'/g, "\\\\'")}')">
              <span>🛒</span> <span>${t.btn_quick_buy_med || 'Buy in Pharmacy'}</span>
            </button>
            <button type="button" class="btn btn-secondary btn-sm" style="color: #065f46; border-color: #a7f3d0; background: #f0fdf4; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; font-size: 0.82rem; padding: 6px 12px;" onclick="addMedicationToDailyScheduleFromEncoded('${encodedMed}')">
              <span>➕</span> <span>${t.btn_add_to_tracker || 'Add to Daily Checklist'}</span>
            </button>
          </div>
          <span class="text-xs" style="color: #64748b; font-weight: 600;">
            ✓ Genuine Certified Pharmacy Brand
          </span>
        </div>
      </div>
    `;
  }).join("");

  const downloadGuideHtml = `
    <div style="margin-top: 14px; background: linear-gradient(135deg, #f0fdfa, #e0f2fe); border: 1.5px solid #0284c7; border-radius: 8px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
      <div>
        <strong style="color: #0369a1; font-size: 0.92rem;">
          📄 Download Full Pharmacy Prescription & Intake Timetable (PDF)
        </strong>
        <div class="text-xs" style="color: #0284c7;">
          Includes Section 5b with verified daily medicine intake timing & meal instructions to buy at any local pharmacy.
        </div>
      </div>
      <a href="${pdfUrl || '#'}" class="btn btn-primary btn-sm" download style="background: #0369a1; border-color: #0369a1; font-weight: 700;">
        📥 Download Pharmacy Guide PDF
      </a>
    </div>
  `;

  container.innerHTML = rowsHtml + downloadGuideHtml;
}

function quickBuyPrescriptionMedicine(medName, pharmacyMatch) {
  if (!pharmacyCatalog || pharmacyCatalog.length === 0) {
    showToast("Loading pharmacy catalog...", "info");
    return;
  }

  const queryTerms = (pharmacyMatch || medName).toLowerCase().replace(/[^a-z0-9\\s]/g, ' ').split(/\\s+/).filter(w => w.length > 2);

  let match = pharmacyCatalog.find(p => {
    const pName = p.name.toLowerCase();
    const pDesc = (p.description || "").toLowerCase();
    const pCat = (p.category || "").toLowerCase();
    return queryTerms.some(term => pName.includes(term) || pDesc.includes(term) || pCat.includes(term));
  });

  if (!match) {
    match = pharmacyCatalog[0];
  }

  if (match) {
    addToCart(match.id);
    const tabBtn = document.getElementById("header-box-meds") || document.querySelector('[data-tab="tab-medications"]');
    if (tabBtn) tabBtn.click();
    const storeSec = document.getElementById("pharmacy-store-section");
    if (storeSec) {
      setTimeout(() => {
        storeSec.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 150);
    }
    showToast(`🛒 Added ${match.name} (₹${match.price.toFixed(2)}) to your pharmacy cart!`, "success");
  } else {
    showToast(`Could not find direct match for ${medName} in stock.`, "warning");
  }
}

async function addMedicationToDailyScheduleFromEncoded(encodedStr) {
  try {
    const med = JSON.parse(decodeURIComponent(encodedStr));
    let schedTime = "08:30 AM";
    const timingLower = (med.timing || "").toLowerCase();
    if (timingLower.includes("night") && !timingLower.includes("morning")) {
      schedTime = "09:00 PM";
    } else if (timingLower.includes("afternoon")) {
      schedTime = "01:30 PM";
    }

    const payload = {
      name: med.name,
      dosage: med.dosage || "As advised",
      frequency: med.frequency || med.timing || "Daily",
      scheduled_time: schedTime,
      condition_target: med.condition_target || "Clinical Treatment",
      instructions: `${med.meal_relation || ''} • ${med.instructions || ''}`.trim()
    };

    const res = await fetch("/api/medications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(`✅ Added ${med.name} to today's Daily Medication To-Do list!`, "success");
      loadMedications();
      const chimeBtn = document.getElementById("btn-simulate-sound-chime");
      if (chimeBtn) chimeBtn.click();
    } else {
      showToast(data.message || "Failed to add medication.", "danger");
    }
  } catch (err) {
    showToast("Error adding medication: " + err.message, "danger");
  }
}

"""

if "function renderPrescribedMedications" not in js:
    js = js.replace("async function loadReportsHistory() {", med_functions + "async function loadReportsHistory() {", 1)
    print("Added renderPrescribedMedications functions.")

# 3. Update renderPharmacyGrid to use translated buttons
pharm_add_btn = """<span>${TRANSLATIONS[currentLanguage]?.btn_add_to_cart || 'Add to Cart'}</span>"""
pharm_rem_btn = """🗑️ ${TRANSLATIONS[currentLanguage]?.btn_remove_item || 'Remove'}"""

js = re.sub(r'<span>Add to Cart</span>', pharm_add_btn, js)
js = re.sub(r'🗑️ Remove', pharm_rem_btn, js)

# 4. Update renderHospitalsGrid to use translated buttons & badges
hosp_buttons_old = """<span>🧭</span> <span>Directions</span>"""
hosp_buttons_new = """<span>🧭</span> <span>${TRANSLATIONS[currentLanguage]?.btn_directions || 'Directions'}</span>"""
js = js.replace(hosp_buttons_old, hosp_buttons_new)

hosp_book_old = """<span>🎫</span> <span>Book OPD Token</span>"""
hosp_book_new = """<span>🎫</span> <span>${TRANSLATIONS[currentLanguage]?.btn_book_opd || 'Book OPD Token'}</span>"""
js = js.replace(hosp_book_old, hosp_book_new)

hosp_focus_old = """<span>🗺️</span> <span>Focus</span>"""
hosp_focus_new = """<span>🗺️</span> <span>${TRANSLATIONS[currentLanguage]?.btn_focus_map || 'Focus'}</span>"""
js = js.replace(hosp_focus_old, hosp_focus_new)

hosp_amb_old = """<span>🚨</span> <span>Ambulance</span>"""
hosp_amb_new = """<span>🚨</span> <span>${TRANSLATIONS[currentLanguage]?.btn_ambulance || 'Ambulance'}</span>"""
js = js.replace(hosp_amb_old, hosp_amb_new)

# 5. Expose on window
window_exports = """
window.quickBuyPrescriptionMedicine = quickBuyPrescriptionMedicine;
window.addMedicationToDailyScheduleFromEncoded = addMedicationToDailyScheduleFromEncoded;
window.renderPrescribedMedications = renderPrescribedMedications;
"""

if "window.quickBuyPrescriptionMedicine" not in js:
    js = js.replace("window.cancelQueueToken = cancelQueueToken;", "window.cancelQueueToken = cancelQueueToken;\n" + window_exports)

with open("static/js/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Patched app.js successfully.")
