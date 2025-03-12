import functools
import os
import re
import json
from flask import Flask, jsonify, render_template, redirect, request, send_from_directory
#rom flask_caching import Cache
from datetime import datetime

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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

# ✅ Route voor gedeelde sessies
@app.route('/shared-chat-sessions')
#@cache.cached(timeout=60)
def shared_chat_sessions():
    with open('data/sessions.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)

    # ✅ Deserialiseren van geserialiseerde data
    for session in sessions:
        for key in ['title', 'description', 'url']:
            if key in session:
                try:
                    session[key] = json.loads(session[key])  # Deserialiseren
                except (json.JSONDecodeError, TypeError):
                    # Als al correct of niet nodig, ga verder
                    pass

        if 'description' in session:
            session['description'] = clean_and_truncate(session['description'])

    # ✅ Sorteer op datum (oudste eerst) en vervolgens omkeren voor nieuwste onderaan
    sessions = sorted(
        sessions,
        key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
        reverse=False
    )

    return render_template('shared-chat-sessions.html', sessions=sessions)


# ✅ Route voor ophalen van sessies
@app.route('/sessions')
#@cache.cached(timeout=60)
def get_sessions():
    with open('data/sessions.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)

    # ✅ Pas clean_and_truncate toe op elk tekstveld (indien aanwezig)
    for session in sessions:
        if 'description' in session:
            session['description'] = clean_and_truncate(session['description'])

    # ✅ Sorteer op datum (oudste eerst) en vervolgens omkeren voor nieuwste onderaan
    sessions = sorted(
        sessions,
        key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'),
        reverse=False
    )

    return jsonify(sessions)



@app.route('/')
#@cache.cached(timeout=60)  # Cache voor 60 seconden
def home():
    return render_template("index.html")


@app.route('/nl/')
#@cache.cached(timeout=60)  # Cache voor 60 seconden
def home_nl():
    return render_template("nl/index.html")


@app.route('/robots.txt')
#@cache.cached(timeout=60)  # Cache voor 60 seconden
def robots():
    """Serveert robots.txt als statisch bestand"""
    return send_from_directory('static', 'robots.txt')


@app.route('/sitemap.xml')
#@cache.cached(timeout=60)  # Cache voor 60 seconden
def sitemap():
    """Serveert sitemap.xml als statisch bestand"""
    return send_from_directory('static', 'sitemap.xml')


@app.route('/<path:path>')
def catch_all(path):
    if request.host == "gpt.proseo.tech":
        return redirect("https://chatgpt.com/g/g-67a9c0b376d881918b85c637d77761f0-pro-seo-assistant", code=301)
    return "This is the Shark App", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
