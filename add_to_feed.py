import json
import os
import re
from datetime import datetime

# Pad naar het JSON-bestand
FILE_PATH = 'data/sessions.json'

# Functie om input op te schonen en af te kappen
def clean_and_truncate(text, length=200):
    text = re.sub(r'\s+', ' ', text.strip())  # Verwijder dubbele spaties
    if len(text) > length:
        truncated = text[:length].rsplit(' ', 1)[0] + '...'
        return truncated
    return text

# Functie om geldige datum te controleren
def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Functie om geldige URL te controleren
def validate_url(url):
    return re.match(r'https?://[\w.-]+(?:\.[\w.-]+)+[/#?]?.*', url) is not None

# Prompt voor invoer
title = input('Titel: ').strip()
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')

import sys

print('Beschrijving (eindig met Ctrl+D of Ctrl+Z):')
print('Voer beschrijving in (typ "END" op een nieuwe regel om te stoppen):')
description_lines = []
while True:
    line = input()
    if line.strip().upper() == 'END':
        break
    description_lines.append(line.strip())
description = ' '.join(description_lines).strip().replace('\n', ' ').replace('\r', ' ')
description = clean_and_truncate(description)

try:
    url = sys.stdin.readline().strip()
    while not validate_url(url):
        print('❌ Ongeldige URL, probeer opnieuw.')
        url = input('URL: ').strip()
except EOFError:
    print('\n🚨 Invoer geannuleerd. Geen gegevens opgeslagen.')
    exit(1)

# Nieuwe record maken
new_record = {
    'title': title,
    'date': date,
    'description': description,
    'url': url
}

# Bestaande JSON laden of nieuw bestand maken
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []
else:
    data = []

# Record toevoegen
data.append(new_record)

# Opslaan naar JSON-bestand
with open(FILE_PATH, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print('\n✅ Record toegevoegd!')
print(json.dumps(new_record, indent=4, ensure_ascii=False))
