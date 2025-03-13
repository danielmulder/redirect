import os
import json
import re
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Logging instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Proxy-lijst (VS)
PROXIES = [
    "http://23.95.255.103:6687",
    "http://31.58.10.48:6016",
    "http://31.58.10.190:6158",
    "http://45.38.70.131:7069",
    "http://104.168.8.85:5538",
]

# ✅ Paden voor opslag
SCREENSHOT_DIR = os.path.join('static', 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ✅ Pad naar JSON-bestand
FILE_PATH = 'data/sessions.json'


# ✅ Functie om geldige URL te controleren
def validate_url(url):
    return re.match(r'https?://[\w.-]+(?:\.[\w.-]+)+[/#?]?.*', url) is not None


# ✅ Functie om screenshot + thumbnail te genereren
def generate_screenshot(url, filename_prefix):
    try:
        # Proxy instellen
        proxy = random.choice(PROXIES)
        logger.info(f"🌐 Gebruikte proxy: {proxy}")

        chrome_options = Options()
        chrome_options.add_argument(f"--proxy-server={proxy}")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ✅ Chrome starten
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ✅ User-Agent instellen
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument(f'user-agent={user_agent}')

        # ✅ Pagina ophalen
        logger.info(f"🌍 URL openen: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # ✅ Bestandsnamen bepalen
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"{filename_prefix}_scrshot_desktop.png")
        thumb_file = os.path.join(SCREENSHOT_DIR, f"{filename_prefix}_thumb_desktop.png")

        # ✅ Screenshot maken
        logger.info(f"📸 Screenshot opslaan als: {screenshot_file}")
        driver.save_screenshot(screenshot_file)

        # ✅ Thumbnail maken (gebruik PIL)
        from PIL import Image
        image = Image.open(screenshot_file)
        image.thumbnail((400, 300))  # Thumbnail formaat
        image.save(thumb_file)

        logger.info(f"🖼️ Thumbnail opgeslagen als: {thumb_file}")

        return screenshot_file.replace("\\", "/")

    except Exception as e:
        logger.error(f"❌ Fout bij het renderen van {url}: {e}")
        return None

    finally:
        if driver:
            driver.quit()


# ✅ JSON updaten met screenshot URL
def update_json():
    if not os.path.exists(FILE_PATH):
        logger.error("❌ JSON-bestand niet gevonden!")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            logger.error("❌ Ongeldig JSON-bestand!")
            return

    updated = False

    for item in data:
        target_url = item.get('target_url')
        if target_url:
            logger.info(f"🔎 Screenshot genereren voor: {target_url}")

            # ✅ Bestandsnaam afleiden uit URL
            filename_prefix = target_url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.',
                                                                                                                  '_')

            # ✅ Screenshot genereren
            screenshot_path = generate_screenshot(target_url, filename_prefix)

            if screenshot_path:
                item['og_img'] = f"/{screenshot_path}"  # 🔥 Bestandspad toevoegen aan JSON
                updated = True
                logger.info(f"✅ Screenshot toegevoegd aan record: {screenshot_path}")

    if updated:
        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            logger.info("✅ JSON-bestand bijgewerkt!")


# ✅ Hoofdprogramma
if __name__ == "__main__":
    logger.info("🚀 Start JSON update en screenshot generatie...")
    update_json()
    logger.info("✅ JSON update voltooid!")
