import os
import json
import logging
from flask import Flask, jsonify, render_template, redirect, request, send_from_directory
from models.model import db
from includes.auth import authenticate_request
from routers.pages_router import pages_router
from includes.utils_class import clean_and_truncate, parse_date
from templates.partials.footer import render_footer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'site_db.db')
SCREENSHOT_PATH = os.path.join(BASE_DIR, 'static', 'screenshots')
THUMBNAIL_SIZE = (400, 300)

def create_app():
    """
    Application Factory for the Flask App.
    """
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Register blueprints for each API module
    app.register_blueprint(pages_router)

    db.init_app(app)

    with app.app_context():
        db.create_all()

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

    return app
