import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from PIL import Image
import logging
from models.model import db, SessionFeed
from app import create_app
from includes.utils_class import parse_date, clean_and_truncate

# ✅ Loggen instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Pad voor screenshots
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCREENSHOT_PATH = os.path.join(BASE_DIR, '..', 'static', 'screenshots')
THUMBNAIL_SIZE = (400, 300)

os.makedirs(SCREENSHOT_PATH, exist_ok=True)

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

        # ✅ Screenshot maken en bestand opslaan
        driver.save_screenshot(screenshot_file)
        logger.info(f"📸 Screenshot opgeslagen als: {screenshot_file}")

        # ✅ Thumbnail genereren met Pillow
        with Image.open(screenshot_file) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumbnail_file)
            logger.info(f"🖼️ Thumbnail opgeslagen als: {thumbnail_file}")

        # ✅ Geef de volledige URL terug voor gebruik in de database
        return (
            f"https://proseo.tech/static/screenshots/{screenshot_filename}",
            f"https://proseo.tech/static/screenshots/{thumbnail_filename}"
        )

    except Exception as e:
        logger.error(f"❌ Fout bij het maken van screenshot: {e}")
        return None, None

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

        preview_image, thumbnail = take_screenshot(driver, url)

        driver.quit()

        return preview_image, thumbnail

    except Exception as e:
        logger.error(f"❌ Fout bij het renderen van {url}: {e}")
        return None, None

# ✅ Flask context activeren
app = create_app()
with app.app_context():
    # ✅ Prompt voor invoer
    title = input('Titel: ').strip()
    date = datetime.today().strftime('%Y-%m-%d')  # ✅ Datum zonder tijd

    # ✅ Beschrijving invoeren
    print('Voer beschrijving in (typ "END" op een nieuwe regel om te stoppen):')
    description_lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        description_lines.append(line.strip())
    description = ' '.join(description_lines).strip()
    summary = clean_and_truncate(description, length=167)  # ✅ Max 167 tekens

    # ✅ Invoer voor URL (hoofdlijst-url)
    url = input('Voer de hoofd-URL in: ').strip()
    target_url = input('Voer de target URL in (optioneel): ').strip()
    if target_url:
        target_url = clean_and_truncate(target_url, length=57)  # ✅ Max 57 tekens

    # ✅ Screenshot genereren (optioneel)
    preview_image, thumbnail = None, None
    if target_url:
        logger.info(f"🌐 Genereren van screenshot voor {target_url}")
        preview_image, thumbnail = render_and_capture(target_url)

    if not preview_image or not thumbnail:
        logger.error("❌ Screenshot mislukt, record wordt NIET opgeslagen.")
        exit(1)

    # ✅ Record aanmaken
    try:
        new_session = SessionFeed(
            created_at=parse_date(date),  # ✅ Datum zonder tijd
            share_link=url,
            target_link=target_url if target_url else None,
            report_title=title,
            summary=summary,
            preview_image=preview_image,
            thumbnail=thumbnail
        )
        db.session.add(new_session)
        db.session.commit()
        logger.info("✅ Record toegevoegd aan de database!")

    except Exception as e:
        logger.error(f"❌ Fout bij opslaan in database: {e}")
        db.session.rollback()
