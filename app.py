from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DB_NAME = "visitors.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_name TEXT,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            consent_given INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_visitor(visitor_name, ip_address, user_agent, consent_given):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO visitors (visitor_name, ip_address, user_agent, consent_given, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        visitor_name,
        ip_address,
        user_agent,
        1 if consent_given else 0,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_visitors():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, visitor_name, ip_address, user_agent, consent_given, created_at
        FROM visitors
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "Unknown"


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    visitor_name = request.form.get("visitor_name", "").strip()
    consent = request.form.get("consent")
    consent_given = consent == "yes"

    if not consent_given:
        flash("You must give consent before proceeding.")
        return redirect(url_for("home"))

    ip_address = get_client_ip()
    user_agent = request.headers.get("User-Agent", "Unknown")

    if not visitor_name:
        visitor_name = "Anonymous"

    save_visitor(visitor_name, ip_address, user_agent, consent_given)
    return render_template(
        "success.html",
        visitor_name=visitor_name,
        ip_address=ip_address
    )


@app.route("/visitors", methods=["GET"])
def visitors():
    rows = get_visitors()
    return render_template("visitors.html", visitors=rows)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
