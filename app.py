import os
import mysql as mysql
from flask import Flask, render_template, redirect, request, jsonify

app = Flask(__name__)

def get_db_config():
    return {
        "host": os.environ.get("gE_MySQL_server"),
        "user": os.environ.get("gE_MySQL_user"),
        "password": os.environ.get("gE_MySQL_password"),
        "database": os.environ.get("gE_MySQL_database"),
        "port": int(os.environ.get("gE_MySQL_port", 25060)),
        "use_pure": True,
        "auth_plugin": "mysql_native_password",
        "ssl_disabled": False  # DigitalOcean vereist SSL
    }

@app.route("/api/test_db")
def test_db():
    """Test de verbinding met de database"""
    db_config = get_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT NOW() as current_time;")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return jsonify({"status": "ok", "db_time": result}), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500

if __name__ == "__main__":
    app.run(debug=True)

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
