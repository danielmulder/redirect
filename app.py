import os
import re
import json
import functools
from datetime import datetime
from flask import Flask, jsonify, render_template, redirect, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from templates.partials.filter import truncate_url
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from PIL import Image
import logging

# ✅ Logging instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ App-configuratie
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'site_db.db')

# ✅ Pad voor screenshots
SCREENSHOT_PATH = "../static/screenshots"
THUMBNAIL_SIZE = (400, 300)

# ✅ Zorg dat de map bestaat
os.makedirs(SCREENSHOT_PATH, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Database-initialisatie
db = SQLAlchemy(app)


class SessionFeed(db.Model):
    __tablename__ = 'sessions_feed'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    share_link = db.Column(db.Text, nullable=False)
    target_link = db.Column(db.Text, nullable=True)
    report_title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    preview_image = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.Text, nullable=True)


# ✅ Decorator voor pagination
class PaginationDecorator:
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.offset = 0

    def set_paging_params(self):
        self.page = int(request.view_args.get('page', self.page) or self.page)
        self.per_page = int(request.view_args.get('per_page', self.per_page) or self.per_page)

        if self.page < 1 or self.per_page < 1 or self.per_page > 100:
            return jsonify({"error": "Invalid pagination values. Page must be ≥ 1 and per_page between 1-100."}), 400

        self.offset = (self.page - 1) * self.per_page

        print(f"per_page: {self.per_page}")


# ✅ Database aanmaken als die nog niet bestaat
#@app._got_first_request
def create_tables():
    if not os.path.exists(DB_PATH):
        logger.info("📁 SQLite database wordt aangemaakt...")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db.create_all()


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


# 🔥 Decorator voor opschonen van JSON en tekst
def clean_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, list):
            # Opschonen van elk JSON-object in de lijst
            cleaned_result = [
                {k: re.sub(r'\s+', ' ', str(v).strip()) if isinstance(v, str) else v for k, v in item.items()}
                for item in result
            ]
            return cleaned_result
        elif isinstance(result, str):
            # Opschonen van tekstresultaat
            return re.sub(r'\s+', ' ', result.strip())
        else:
            return result
    return wrapper


# ✅ Tekst opschonen en inkorten
@clean_data
def clean_and_truncate(text, length=200):
    if len(text) > length:
        truncated = text[:length].rsplit(' ', 1)[0] + '...'
        return truncated
    return text


# ✅ Geldige datum parser
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None


# ✅ Route voor shared sessions met paginering
@app.route('/shared-chat-sessions/')
@app.route('/shared-chat-sessions/<int:page>/')
@app.route('/shared-chat-sessions/<int:page>/<int:per_page>/')
def shared_chat_sessions(page=1, per_page=10):
    paginator = PaginationDecorator()
    paginator.page = page
    paginator.per_page = per_page
    paginator.set_paging_params()

    # ✅ Query uit SQLite database met LIMIT en OFFSET
    sessions = SessionFeed.query \
        .order_by(SessionFeed.created_at.desc()) \
        .limit(paginator.per_page) \
        .offset(paginator.offset) \
        .all()

    # ✅ Totaal aantal sessies ophalen
    total_sessions = SessionFeed.query.count()
    total_pages = (total_sessions + paginator.per_page - 1) // paginator.per_page

    return render_template(
        'shared-chat-sessions.html',
        sessions=sessions,
        total_pages=total_pages,
        current_page=paginator.page,
        per_page=paginator.per_page  # ✅ per_page toevoegen aan context
    )


# ✅ Route voor ophalen van sessies
@app.route('/sessions')
def get_sessions():
    with open('data/sessions.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)

    for session in sessions:
        if 'description' in session:
            session['description'] = clean_and_truncate(session['description'])

        if 'date' in session:
            session['date'] = parse_date(session['date'])

    sessions = sorted(
        [s for s in sessions if s.get('date')],
        key=lambda x: x['date'],
        reverse=True
    )

    return jsonify(sessions)


# ✅ Standaard routes
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


@app.route('/<path:path>')
def catch_all(path):
    if request.host == "gpt.proseo.tech":
        return redirect("https://chatgpt.com/g/g-67a9c0b376d881918b85c637d77761f0-pro-seo-assistant", code=301)
    return "This is the Shark App", 200


# ✅ App starten
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
