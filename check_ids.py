import re

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

ids = re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", js_text)
unique_ids = set(ids)

missing_ids = []
for i in unique_ids:
    if f'id="{i}"' not in html_text and f"id='{i}'" not in html_text:
        missing_ids.append(i)

print('IDs in JS but missing in HTML:', missing_ids)
