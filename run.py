"""
run.py – One-command startup for Wanderlust Travel Agency
Run: python run.py
"""
import os
import sys
import subprocess
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database.db')

# ── Step 1: Install dependencies ──────────────────────────────
print("\n[1/3] Installing dependencies from requirements.txt...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                       os.path.join(BASE_DIR, 'requirements.txt')],
                      stdout=subprocess.DEVNULL)
print("      Dependencies ready.")

# ── Step 2: Initialise database ───────────────────────────────
print("[2/3] Setting up database...")
try:
    from flask import Flask
    app = Flask(__name__, root_path=BASE_DIR)
    app.config['SECRET_KEY'] = 'wanderlust-super-secret-2025'

    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    with app.app_context():
        db = get_db()
        tbl = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='packages'").fetchone()
        if not tbl:
            schema_path = os.path.join(BASE_DIR, 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            print("      Database created and seeded with sample data.")
        else:
            print("      Database already exists, skipping init.")
        db.close()
except Exception as e:
    print(f"      Warning: Could not init DB here, app.py will handle it. ({e})")

# ── Step 3: Start Flask server ────────────────────────────────
print("[3/3] Starting Wanderlust server on http://127.0.0.1:5000 ...")
print("      Press Ctrl+C to stop.\n")
os.chdir(BASE_DIR)
os.system(f'{sys.executable} app.py')
