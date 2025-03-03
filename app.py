import os
from flask import Flask, render_template, redirect, request

app = Flask(__name__)

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
