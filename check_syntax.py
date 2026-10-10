# check_syntax.py
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

print('File characters:', len(content))
print('Has TRANSLATIONS:', 'const TRANSLATIONS =' in content)
print('Has applyLanguage:', 'function applyLanguage(lang)' in content)
print('Has renderPrescribedMedications:', 'function renderPrescribedMedications' in content)
print('Has quickBuyPrescriptionMedicine:', 'function quickBuyPrescriptionMedicine' in content)
print('Has addMedicationToDailyScheduleFromEncoded:', 'function addMedicationToDailyScheduleFromEncoded' in content)
