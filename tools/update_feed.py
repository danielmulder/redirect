import os
import re
import time
import functools
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from PIL import Image
import logging
from models.model import db, SessionFeed
from app import create_app

# ✅ Loggen instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Pad voor screenshots
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCREENSHOT_PATH = os.path.join(BASE_DIR, '..', 'static', 'screenshots')
THUMBNAIL_SIZE = (400, 300)

os.makedirs(SCREENSHOT_PATH, exist_ok=True)

# ✅ Valid date parser
def parse_date(date_str):
    try:
        parsed_time = time.strptime(date_str, '%Y-%m-%d')
        # ✅ Omdraaien naar datetime object voor SQLAlchemy
        return datetime(
            year=parsed_time.tm_year,
            month=parsed_time.tm_mon,
            day=parsed_time.tm_mday
        )
    except (ValueError, TypeError):
        return None

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

# ✅ Decorator voor opschonen van tekst
def clean_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, list):
            cleaned_result = [
                {k: re.sub(r'\s+', ' ', str(v).strip()) if isinstance(v, str) else v for k, v in item.items()}
                for item in result
            ]
            return cleaned_result
        elif isinstance(result, str):
            return re.sub(r'\s+', ' ', result.strip())
        else:
            return result
    return wrapper

# ✅ Clean en afkappen tekst
@clean_data
def clean_and_truncate(text, length=200):
    if len(text) > length:
        truncated = text[:length].rsplit(' ', 1)[0] + '...'
        return truncated
    return text

# ✅ Flask context activeren
app = create_app()
with app.app_context():
    # ✅ Prompt voor invoer
    title = input('Titel: ').strip()

    # ✅ Datum invoeren
    date_str = input('Datum (YYYY-MM-DD): ').strip()
    date = parse_date(date_str)
    if not date:
        print("❌ Ongeldige datum! Probeer opnieuw.")
        exit(1)

    # ✅ Beschrijving invoeren
    print('Voer beschrijving in (typ "END" op een nieuwe regel om te stoppen):')
    description_lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        description_lines.append(line.strip())
    description = ' '.join(description_lines).strip()

    # ✅ Invoer voor URL (hoofdlijst-url)
    url = input('Voer de hoofd-URL in: ').strip()
    target_url = input('Voer de target URL in (optioneel): ').strip()

    # ✅ Screenshot genereren
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
            created_at=date,
            share_link=url,
            target_link=target_url if target_url else None,
            report_title=title,
            summary=description,
            preview_image=preview_image,
            thumbnail=thumbnail
        )
        db.session.add(new_session)
        db.session.commit()
        logger.info("✅ Record toegevoegd aan de database!")

    except Exception as e:
        logger.error(f"❌ Fout bij opslaan in database: {e}")
        db.session.rollback()

