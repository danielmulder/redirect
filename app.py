import os
import base64
import secrets
from flask import Flask, render_template, request, Response, redirect, g

app = Flask(__name__)

def generate_nonce():
    """Genereert een veilige, willekeurige nonce."""
    return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')


@app.before_request
def set_nonce():
    """Slaat de nonce op in Flask's request context (`g`)."""
    g.nonce = generate_nonce()


@app.after_request
def add_security_headers(response: Response):
    """Voegt security headers met nonce toe aan elke response."""
    csp_policy = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{g.nonce}'; "
        f"style-src 'self' 'nonce-{g.nonce}'; "
        f"img-src 'self' data:; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
    )
    response.headers["Content-Security-Policy"] = csp_policy
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return response


@app.route('/')
def home():
    """Rendert index.html en voegt nonce toe aan de template."""
    return render_template("index.html", nonce=g.nonce)


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
