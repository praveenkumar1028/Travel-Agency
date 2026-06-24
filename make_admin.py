"""
make_admin.py – Promote a registered user to admin role
Usage: python make_admin.py your@email.com
"""
import sys, sqlite3, os

if len(sys.argv) < 2:
    print("Usage: python make_admin.py <email>")
    sys.exit(1)

email = sys.argv[1]
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

if not os.path.exists(db_path):
    print("Error: database.db not found. Run 'python run.py' first.")
    sys.exit(1)

db = sqlite3.connect(db_path)
user = db.execute("SELECT id, name, role FROM users WHERE email=?", (email,)).fetchone()

if not user:
    print(f"Error: No user found with email '{email}'.")
    db.close()
    sys.exit(1)

if user[2] == 'admin':
    print(f"'{user[1]}' ({email}) is already an admin.")
else:
    db.execute("UPDATE users SET role='admin' WHERE email=?", (email,))
    db.commit()
    print(f"Success! '{user[1]}' ({email}) has been promoted to admin.")
    print("Restart the Flask server and log in to access /admin")

db.close()
