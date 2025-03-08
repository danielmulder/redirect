import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/robots.txt')
def robots():
    """Serveert robots.txt als statisch bestand"""
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
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