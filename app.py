from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file, flash, get_flashed_messages
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# HELPERS
# -------------------------

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_greeting():
    h = datetime.now().hour
    if h < 12:   return "Good morning"
    if h < 17:   return "Good afternoon"
    if h < 21:   return "Good evening"
    return "Good night"

# -------------------------
# DATABASE SETUP
# -------------------------

def init_db():
    conn = sqlite3.connect("forensic.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        hash TEXT,
        upload_time TEXT,
        file_size INTEGER DEFAULT 0,
        file_type TEXT DEFAULT ''
    )
    """)

    # Migrate existing DB — add columns if missing
    existing = [row[1] for row in cursor.execute("PRAGMA table_info(records)").fetchall()]
    if "file_size" not in existing:
        cursor.execute("ALTER TABLE records ADD COLUMN file_size INTEGER DEFAULT 0")
    if "file_type" not in existing:
        cursor.execute("ALTER TABLE records ADD COLUMN file_type TEXT DEFAULT ''")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("forensic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM records")
    total_files = cursor.fetchone()[0]
    cursor.execute("SELECT upload_time FROM records ORDER BY id DESC LIMIT 1")
    last_row = cursor.fetchone()
    last_upload = last_row[0] if last_row else None
    cursor.execute("SELECT SUM(file_size) FROM records")
    total_size_raw = cursor.fetchone()[0] or 0
    conn.close()
    return render_template(
        "index.html",
        total_files=total_files,
        last_upload=last_upload,
        total_size=format_size(total_size_raw),
        greeting=get_greeting()
    )

# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("forensic.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------------
# UPLOAD
# -------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename != "":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            file_size = os.path.getsize(filepath)
            ext = os.path.splitext(file.filename)[1].lower().lstrip('.') or 'unknown'

            sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            file_hash = sha256.hexdigest()
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect("forensic.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO records (filename, hash, upload_time, file_size, file_type) VALUES (?, ?, ?, ?, ?)",
                (file.filename, file_hash, upload_time, file_size, ext)
            )
            conn.commit()
            conn.close()

            flash(f"✓ '{file.filename}' uploaded and hashed successfully.", "success")
            return redirect(url_for("logs"))
        else:
            flash("No file selected.", "error")

    return render_template("upload.html")

# -------------------------
# VERIFY
# -------------------------

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None
    result_type = None
    verified_hash = None

    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename != "":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()
            verified_hash = file_hash

            conn = sqlite3.connect("forensic.db")
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM records WHERE filename=?", (file.filename,))
            record = cursor.fetchone()
            conn.close()

            if record:
                if file_hash == record[0]:
                    result = "File is Authentic"
                    result_type = "authentic"
                else:
                    result = "File has been Modified"
                    result_type = "modified"
            else:
                result = "No record found for this file"
                result_type = "notfound"
        else:
            flash("No file selected.", "error")

    return render_template("verify.html", result=result, result_type=result_type, verified_hash=verified_hash)

# -------------------------
# LOGS
# -------------------------

@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("forensic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, hash, upload_time, file_size, file_type FROM records ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()

    # Enrich records with formatted size
    enriched = []
    for row in records:
        size_fmt = format_size(row[4]) if row[4] else "—"
        enriched.append(row + (size_fmt,))

    return render_template("logs.html", records=enriched)

# -------------------------
# DELETE RECORD
# -------------------------

@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    if "user" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("forensic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM records WHERE id=?", (record_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
        conn.commit()
        flash(f"Record #{record_id} ({row[0]}) deleted.", "info")
    conn.close()
    return redirect(url_for("logs"))

# -------------------------
# REPORT
# -------------------------

@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("forensic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, hash, upload_time, file_size, file_type FROM records ORDER BY id")
    records = cursor.fetchall()
    conn.close()

    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "ForensicVault — Digital Evidence Report")
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(40, height - 68, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   |   Total Records: {len(records)}")
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.line(40, height - 78, width - 40, height - 78)

    y = height - 100
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40,  y, "ID")
    c.drawString(70,  y, "FILENAME")
    c.drawString(240, y, "SHA-256 (first 32 chars)")
    c.drawString(460, y, "SIZE")
    c.drawString(510, y, "UPLOADED AT")
    y -= 6
    c.line(40, y, width - 40, y)
    y -= 14

    c.setFont("Helvetica", 8)
    for row in records:
        if y < 60:
            c.showPage()
            y = height - 60
        c.setFillColorRGB(0, 0, 0)
        c.drawString(40,  y, str(row[0]))
        c.drawString(70,  y, str(row[1])[:28])
        c.drawString(240, y, str(row[2])[:32] + "…")
        c.drawString(460, y, format_size(row[4]) if row[4] else "—")
        c.drawString(510, y, str(row[3]))
        y -= 16
        c.setStrokeColorRGB(0.93, 0.93, 0.93)
        c.line(40, y + 2, width - 40, y + 2)

    c.save()
    return send_file(pdf_path, as_attachment=True)

# -------------------------
# FINGERPRINT
# -------------------------

@app.route('/fingerprint', methods=['GET', 'POST'])
def fingerprint():
    if "user" not in session:
        return redirect(url_for("login"))

    file_info = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != "":
            file_bytes = file.read()
            file_info = {
                "name":   file.filename,
                "sha256": hashlib.sha256(file_bytes).hexdigest(),
                "sha1":   hashlib.sha1(file_bytes).hexdigest(),
                "md5":    hashlib.md5(file_bytes).hexdigest(),
                "size":   len(file_bytes),
                "size_fmt": format_size(len(file_bytes)),
                "ext":    os.path.splitext(file.filename)[1].lower().lstrip('.') or 'unknown',
            }
        else:
            flash("No file selected.", "error")

    return render_template("fingerprint.html", file_info=file_info)

if __name__ == "__main__":
    app.run(debug=True)
