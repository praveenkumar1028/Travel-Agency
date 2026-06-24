# 🌍 Wanderlust Travel Agency

A **fully dynamic, production-ready** travel agency web application built with Flask, SQLite, Jinja2, and vanilla JavaScript.

---

## ✨ Features

| Module | What's included |
|---|---|
| 🏠 **Home Page** | Hero, animated stats, featured packages, testimonials, blog preview, newsletter, footer |
| 🗺️ **Packages** | All packages from DB, category filter, search, wishlist toggle |
| 📦 **Package Detail** | Full description, reviews, rating, related packages, book sidebar, wishlist |
| 📅 **Booking** | Live summary sidebar, package dropdown from DB, date picker |
| 👤 **Dashboard** | Bookings history, wishlist, written reviews — all in tabbed view |
| ✏️ **Profile** | Edit name, phone, country |
| 📝 **Blog** | Blog listing + individual post pages |
| 📞 **Contact** | Contact form saved to DB |
| ℹ️ **About** | Team, mission, timeline |
| 🔐 **Auth** | Register, login, logout (session-based, bcrypt hashing) |
| 🛡️ **Admin Panel** | Add/edit/delete packages, view users, bookings, reviews, contacts, logs |
| 🔌 **REST API** | `/api/packages`, `/api/bookings`, `/api/book`, `/api/search` |

---

## 🚀 Quick Start (Anyone Can Run This)

### Prerequisites
- **Python 3.10+** → https://www.python.org/downloads/
- No other installs needed — everything is handled automatically.

### Run in 3 steps

```bash
# 1. Clone / unzip the project folder
cd travel-agency

# 2. Run the one-command startup script
python run.py

# 3. Open your browser
# http://127.0.0.1:5000
```

`run.py` will automatically:
- ✅ Install all Python dependencies from `requirements.txt`
- ✅ Create and seed the SQLite database
- ✅ Start the Flask development server

---

## 📂 Project Structure

```
travel-agency/
│
├── app.py                  # Main Flask app (routes, logic, API)
├── schema.sql              # Database schema + seed data
├── run.py                  # One-command setup & launch
├── requirements.txt        # Python dependencies
│
├── templates/
│   ├── navbar.html         # Shared navigation bar
│   ├── index.html          # Home page
│   ├── packages.html       # All packages + filter
│   ├── package_detail.html # Individual package + reviews
│   ├── booking.html        # Booking form
│   ├── dashboard.html      # User dashboard
│   ├── profile.html        # Edit profile
│   ├── admin.html          # Admin panel
│   ├── blog.html           # Blog listing
│   ├── blog_post.html      # Blog detail
│   ├── contact.html        # Contact form
│   ├── about.html          # About page
│   ├── login.html          # Login
│   └── register.html       # Register
│
└── static/
    ├── style.css           # Premium dark UI
    ├── script.js           # JS helpers, AJAX, animations
    └── images/
        ├── hero.jpg
        ├── maldives.jpg
        ├── switzerland.jpg
        ├── paris.jpg
        ├── dubai.jpg
        └── japan.jpg
```

---

## 🔑 Default Admin Access

After registering, promote your account to admin by running:

```bash
python make_admin.py your@email.com
```

Or run manually:

```python
import sqlite3
db = sqlite3.connect('database.db')
db.execute("UPDATE users SET role='admin' WHERE email='your@email.com'")
db.commit()
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/packages` | List all packages |
| GET | `/api/packages/<id>` | Single package |
| GET | `/api/bookings` | My bookings (auth required) |
| POST | `/api/book` | Create booking (auth required) |
| GET | `/api/search?q=...` | Search packages |

---

## 🛠️ Tech Stack

- **Backend**: Python 3 / Flask 3
- **Database**: SQLite (auto-created, no setup)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (fetch API)
- **Auth**: Session-based + Werkzeug password hashing
- **Fonts**: Google Fonts (Montserrat + Playfair Display)
- **Icons**: Font Awesome 6

---

## 📦 Dependencies

All listed in `requirements.txt`:
```
Flask==3.1.0
Werkzeug==3.1.3
Jinja2==3.1.6
```

Install manually if needed:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment

For production, replace the `SECRET_KEY` in `app.py` with an environment variable:

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

---

## 📄 License

MIT License — free to use and modify.
"# Travel-agency" 
"# Travel-Agency" 
"# Travel-Agency" 
"# Travel-Agency" 
