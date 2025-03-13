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
SCREENSHOT_PATH = "../static/screenshots"
THUMBNAIL_SIZE = (400, 300)  # Formaat van de thumbnail

# Zorg dat de map bestaat
os.makedirs(SCREENSHOT_PATH, exist_ok=True)

# ✅ Bestandsnaam genereren functie
def generate_filename(url, suffix):
    # Verwijder het schema ('https://' of 'http://')
    url_clean = re.sub(r'^https?:\/\/', '', url)
    # Speciale karakters vervangen door '_'
    filename = re.sub(r'[^\w\-_]', '_', url_clean)
    filename = filename.strip('_')  # Eventuele underscores aan het begin/eind verwijderen
    return f"{filename}_{suffix}_desktop.png"

# ✅ Functie om screenshot te maken
def take_screenshot(driver, url):
    try:
        # Bestandsnamen genereren
        screenshot_filename = generate_filename(url, 'scrshot')
        thumbnail_filename = generate_filename(url, 'thumb')

        screenshot_file = os.path.join(SCREENSHOT_PATH, screenshot_filename)
        thumbnail_file = os.path.join(SCREENSHOT_PATH, thumbnail_filename)

        # ✅ Screenshot maken (bestand wordt overschreven als het al bestaat)
        driver.save_screenshot(screenshot_file)
        logger.info(f"📸 Screenshot opgeslagen als: {screenshot_file}")

        # ✅ Thumbnail genereren met Pillow
        with Image.open(screenshot_file) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumbnail_file)
            logger.info(f"🖼️ Thumbnail opgeslagen als: {thumbnail_file}")

        return screenshot_file, thumbnail_file

    except Exception as e:
        logger.error(f"❌ Fout bij het maken van screenshot: {e}")
        return None, None

# ✅ Renderen en screenshot maken
def render_and_parse_page(url):
    try:
        # ✅ Chrome opties voor desktop modus
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # ✅ Desktop User-Agent instellen
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument(f'user-agent={user_agent}')

        # ✅ Start Chrome browser
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ✅ Open de pagina
        logger.info(f"🌐 Openen van URL: {url}")
        driver.get(url)

        # ✅ Screenshot + Thumbnail maken
        screenshot_file, thumbnail_file = take_screenshot(driver, url)

        # ✅ HTML ophalen
        rendered_html = driver.page_source
        logger.info("✅ HTML succesvol opgehaald!")

        # ✅ Sluit browser
        driver.quit()

        return {
            "url": url,
            "screenshot": screenshot_file,
            "thumbnail": thumbnail_file
        }

    except Exception as e:
        logger.error(f"❌ Fout bij het renderen van {url}: {e}")
        return None

# ✅ Testen
if __name__ == "__main__":
    test_url = "https://proseo.tech/"
    parsed_output = render_and_parse_page(test_url)

    if parsed_output:
        print("\n✅ Succesvolle parsing!")
        print(parsed_output)
    else:
        print("❌ Parsing mislukt.")
