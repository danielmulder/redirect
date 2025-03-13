import json
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from PIL import Image
import logging

# ✅ Loggen instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Pad voor screenshots
SCREENSHOT_PATH = "static/screenshots"
THUMBNAIL_SIZE = (400, 300)

# ✅ Zorg dat de map bestaat
os.makedirs(SCREENSHOT_PATH, exist_ok=True)

# ✅ Pad naar het JSON-bestand
FILE_PATH = 'data/sessions.json'

# ✅ Bestandsnaam genereren functie
def generate_filename(url, suffix):
    url_clean = re.sub(r'^https?:\/\/', '', url)
    filename = re.sub(r'[^\w\-_]', '_', url_clean)
    filename = filename.strip('_')
    return f"{filename}_{suffix}_desktop.png"

# ✅ Screenshot + thumbnail maken functie
def take_screenshot(driver, url):
    try:
        screenshot_filename = generate_filename(url, 'scrshot')
        thumbnail_filename = generate_filename(url, 'thumb')

        screenshot_file = os.path.join(SCREENSHOT_PATH, screenshot_filename)
        thumbnail_file = os.path.join(SCREENSHOT_PATH, thumbnail_filename)

        # ✅ Screenshot maken en bestand overschrijven als het al bestaat
        driver.save_screenshot(screenshot_file)
        logger.info(f"📸 Screenshot opgeslagen als: {screenshot_file}")

        # ✅ Thumbnail genereren met Pillow
        with Image.open(screenshot_file) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumbnail_file)
            logger.info(f"🖼️ Thumbnail opgeslagen als: {thumbnail_file}")

        # ✅ Geef de volledige URL terug voor gebruik in JSON
        return f"https://proseo.tech/static/screenshots/{screenshot_filename}"

    except Exception as e:
        logger.error(f"❌ Fout bij het maken van screenshot: {e}")
        return None

# ✅ Pagina renderen en screenshot maken
def render_and_capture(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument(f'user-agent={user_agent}')

        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        logger.info(f"🌐 Openen van URL: {url}")
        driver.get(url)

        og_img = take_screenshot(driver, url)

        driver.quit()

        return og_img

    except Exception as e:
        logger.error(f"❌ Fout bij het renderen van {url}: {e}")
        return None

# ✅ Functie om input op te schonen en af te kappen
def clean_and_truncate(text, length=200):
    text = re.sub(r'\s+', ' ', text.strip())
    if len(text) > length:
        truncated = text[:length].rsplit(' ', 1)[0] + '...'
        return truncated
    return text

# ✅ Functie om geldige URL te controleren
def validate_url(url):
    return re.match(r'https?://[\w.-]+(?:\.[\w.-]+)+[/#?]?.*', url) is not None

# ✅ Prompt voor invoer
title = input('Titel: ').strip()
date = datetime.today().strftime('%Y-%m-%d')

# ✅ Beschrijving invoeren
print('Voer beschrijving in (typ "END" op een nieuwe regel om te stoppen):')
description_lines = []
while True:
    line = input()
    if line.strip().upper() == 'END':
        break
    description_lines.append(line.strip())
description = ' '.join(description_lines).strip()
description = clean_and_truncate(description)

# ✅ Invoer voor URL (hoofdlijst-url)
url = input('Voer de hoofd-URL in: ').strip()
while not validate_url(url):
    print('❌ Ongeldige URL, probeer opnieuw.')
    url = input('URL: ').strip()

# ✅ Invoer voor target_url (directe link)
target_url = input('Voer de target URL in (optioneel): ').strip()
if target_url and not validate_url(target_url):
    print('❌ Ongeldige target URL, probeer opnieuw.')
    target_url = input('Target URL: ').strip()

# ✅ Screenshot genereren als er een target_url is
og_img = None
if target_url:
    logger.info(f"🌐 Genereren van screenshot voor {target_url}")
    og_img = render_and_capture(target_url)

# ✅ Nieuw record maken
new_record = {
    'title': title,
    'date': date,
    'description': description,
    'url': url,
    'target_url': target_url if target_url else None,
    'og_img': og_img if og_img else None  # ✅ Screenshot opslaan in record
}

# ✅ Bestaande JSON laden of nieuw bestand maken
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []
else:
    data = []

# ✅ Record toevoegen
data.append(new_record)

# ✅ Opslaan naar JSON-bestand
with open(FILE_PATH, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

# ✅ Output bevestiging
print('\n✅ Record toegevoegd!')
print(json.dumps(new_record, indent=4, ensure_ascii=False))
