"""
URL Shortener
A lightweight URL shortening service built with Flask and SQLite.
"""

import sqlite3
import string
import random
import io
import base64
import qrcode
from flask import Flask, request, redirect, render_template, jsonify, abort, g
from urllib.parse import quote

app = Flask(__name__)

DATABASE = "urls.db"
SHORT_CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits  # a-z, A-Z, 0-9


# ---------- Database helpers ----------

def get_db():
    """Return a database connection scoped to the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the urls table if it doesn't already exist."""
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                clicks INTEGER DEFAULT 0
            )
            """
        )
        db.commit()


# ---------- Core logic ----------

def generate_short_code(db):
    """Generate a random, unique 6-character short code."""
    while True:
        code = "".join(random.choices(ALPHABET, k=SHORT_CODE_LENGTH))
        existing = db.execute(
            "SELECT id FROM urls WHERE short_code = ?", (code,)
        ).fetchone()
        if not existing:
            return code


def create_short_url(original_url):
    """Create (or reuse) a short code for the given URL."""
    db = get_db()

    existing = db.execute(
        "SELECT short_code FROM urls WHERE original_url = ?", (original_url,)
    ).fetchone()
    if existing:
        return existing["short_code"]

    code = generate_short_code(db)
    db.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
        (code, original_url),
    )
    db.commit()
    return code


def is_valid_url(url):
    """Basic validation - must start with http:// or https://"""
    return url.startswith("http://") or url.startswith("https://")


def generate_qr_base64(data):
    """Generate a QR code for the given data and return it as a base64 PNG string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#4f46e5", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# ---------- Web routes ----------

@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    qr_image = None
    error = None
    output_type = "short"

    if request.method == "POST":
        original_url = request.form.get("url", "").strip()
        output_type = request.form.get("output_type", "short")

        if not original_url:
            error = "Please enter a URL."
        elif not is_valid_url(original_url):
            error = "URL must start with http:// or https://"
        else:
            code = create_short_url(original_url)
            short_url = request.host_url + code

            if output_type == "qr":
                qr_image = generate_qr_base64(short_url)

    return render_template(
        "index.html",
        short_url=short_url,
        qr_image=qr_image,
        output_type=output_type,
        error=error,
    )


@app.route("/<short_code>")
def redirect_to_original(short_code):
    db = get_db()
    row = db.execute(
        "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if row is None:
        abort(404)

    db.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
    )
    db.commit()

    return redirect(row["original_url"])


@app.route("/stats/<short_code>")
def stats(short_code):
    db = get_db()
    row = db.execute(
        "SELECT * FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if row is None:
        abort(404)

    return render_template("stats.html", url=row)


# ---------- JSON API ----------

@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    """
    JSON API endpoint.
    Request body: {"url": "https://example.com"}
    Response: {"short_url": "http://127.0.0.1:5000/abc123"}
    """
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Request body must include a 'url' field"}), 400

    original_url = data["url"].strip()
    if not is_valid_url(original_url):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    code = create_short_url(original_url)
    return jsonify({
        "short_url": request.host_url + code,
        "short_code": code,
        "original_url": original_url
    })


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", debug=True)
