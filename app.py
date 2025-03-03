import os
from flask import Flask, render_template, redirect, request, Response

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    """Voegt security HTTP headers toe aan elke response"""
    response.headers["Cache-Control"] = "public, max-age=31536000"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), fullscreen=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'"
    return response


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/<path:path>')
def catch_all(path):
    # Controleer of de aanvraag van gpt.proseo.tech komt
    if request.host == "gpt.proseo.tech":
        return redirect("https://chatgpt.com/g/g-67a9c0b376d881918b85c637d77761f0-pro-seo-assistant", code=301)

    # Alle andere domeinen blijven zoals ze zijn (zoals app.proseo.tech)
    return "This is the Shark App", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
