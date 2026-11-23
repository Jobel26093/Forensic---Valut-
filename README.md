# ForensicVault

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" />

**A professional Digital Evidence Management System built with Python & Flask.**

[🚀 Features](#-features) · [📸 Screenshots](#-screenshots) · [⚙️ Installation](#️-installation) · [🗂️ Project Structure](#️-project-structure) · [📖 How It Works](#-how-it-works)

</div>

---

## 🧐 What is ForensicVault?

**ForensicVault** is a web-based forensics platform that allows investigators to:

- 📁 **Upload** digital evidence files and generate cryptographic hashes
- 🔍 **Verify** file integrity — instantly detect if a file has been tampered with
- 🧬 **Fingerprint** any file with MD5, SHA-1, and SHA-256 simultaneously
- 📋 **Log** every piece of evidence with a full audit trail
- 📄 **Export** a formatted PDF forensics report

> **Core principle:** Even changing a single byte of a file produces a completely different hash — making tampering immediately detectable.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Login** | Session-based authentication with admin access |
| ☁️ **Evidence Upload** | Drag & drop upload with SHA-256 hashing |
| ✅ **Integrity Verification** | Re-upload any file to check if it was modified |
| 🧬 **File Fingerprint** | Generate MD5, SHA-1 & SHA-256 in one click |
| 📋 **Evidence Logs** | Full audit table with file type icons, size, search & delete |
| 📄 **PDF Report** | Professional forensics report export via ReportLab |
| 🔔 **Toast Notifications** | Real-time success/error feedback on every action |
| 🗑️ **Record Management** | Delete evidence records with confirmation |

---

## 📸 Screenshots

> Login page, Dashboard, Evidence Logs, Fingerprint tool — clean white & black professional UI.

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Jobel26093/Forensic---Valut-.git
cd Forensic---Valut-
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Or if you prefer npm:

```bash
npm run dev
```

### 4. Open in browser

```
http://127.0.0.1:5000
```

**Default credentials:**
| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

---

## 🗂️ Project Structure

```
forensic_project/
│
├── app.py                  # Main Flask app — all routes and logic
├── requirements.txt        # Python dependencies
├── forensic.db             # SQLite database (auto-created on first run)
├── package.json            # npm shim (optional — runs python app.py)
│
├── uploads/                # Uploaded evidence files
│
└── templates/              # Jinja2 HTML templates
    ├── base.html           # Shared layout: navbar, flash toasts
    ├── login.html          # Authentication page
    ├── index.html          # Dashboard with live stats
    ├── upload.html         # Upload evidence with drag & drop
    ├── verify.html         # File integrity checker
    ├── fingerprint.html    # Multi-hash generator
    └── logs.html           # Evidence records table
```

---

## 📖 How It Works

### Upload & Hash

```
User uploads file
      ↓
File saved to /uploads/
      ↓
SHA-256 computed (chunk-by-chunk, memory efficient)
      ↓
Record stored: filename · hash · timestamp · size · type
```

### Verify Integrity

```
User re-uploads the same file
      ↓
New SHA-256 computed
      ↓
Compared against stored hash in database
      ↓
✅ Match     → "File is Authentic"
❌ Mismatch  → "File has been Modified"
❓ No record → "No record found"
```

### File Fingerprint

Computes three hashes at once from the uploaded file:

| Hash | Characters | Use Case |
|------|-----------|----------|
| MD5 | 32 | Legacy compatibility |
| SHA-1 | 40 | Older forensics tools |
| SHA-256 | 64 | Modern standard — most secure |

---

## 🗄️ Database Schema

```sql
-- Evidence records
CREATE TABLE records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT,
    hash        TEXT,         -- SHA-256 hex digest
    upload_time TEXT,         -- YYYY-MM-DD HH:MM:SS
    file_size   INTEGER,      -- bytes
    file_type   TEXT          -- file extension
);

-- Users
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
);
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 + Flask |
| Database | SQLite |
| Hashing | Python `hashlib` |
| PDF Generation | ReportLab |
| Frontend | Jinja2 + Bootstrap 5 + Bootstrap Icons |
| Fonts | Inter (UI) · JetBrains Mono (hashes) |

---

## ⚠️ Security Notes

> This is a **development/demo** build. For production deployment, consider:

- 🔑 Hash passwords with `bcrypt` (currently stored in plain text)
- 🔐 Load `secret_key` from environment variable, not hardcoded
- 📂 Validate and restrict uploaded file types
- 🚫 Set `debug=False` in production
- 🗃️ Migrate to PostgreSQL for multi-user, high-volume use

---

## 📄 License

This project is for educational and demonstration purposes.

---

<div align="center">
Built with ❤️ using Python & Flask
</div>
