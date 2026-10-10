# test_js_quality.py
with open("static/js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Check for any obvious undefined references in applyLanguage
start_apply = js.find("function applyLanguage(lang) {")
end_apply = js.find("function initVoiceReader() {", start_apply)
apply_body = js[start_apply:end_apply]

dangerous_vars = ["analysis.", "data.", "event.", "req.", "resp."]
for dv in dangerous_vars:
    if dv in apply_body:
        print(f"WARNING: Found {dv} in applyLanguage!")
    else:
        print(f"OK: No {dv} in applyLanguage")

# Check window exports
print("Has window exports:", "window.quickBuyPrescriptionMedicine" in js)
