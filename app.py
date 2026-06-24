import os, sqlite3
from datetime import datetime, date
from functools import wraps
from flask import (Flask, render_template, request, redirect,
    url_for, flash, session, g, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wanderlust-super-secret-2025'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database.db')

# ── DB helpers ────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def teardown_db(exc):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()

# ── Decorators ────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def w(*a, **kw):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*a, **kw)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a, **kw):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*a, **kw)
    return w

@app.context_processor
def inject_globals():
    db = get_db()
    wishlist_ids = []
    if 'user_id' in session:
        rows = db.execute('SELECT package_id FROM wishlist WHERE user_id=?', (session['user_id'],)).fetchall()
        wishlist_ids = [r['package_id'] for r in rows]
    return {'now_date': date.today().isoformat(), 'wishlist_ids': wishlist_ids}

# ── PUBLIC ROUTES ─────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    featured = [dict(r) for r in db.execute('SELECT * FROM packages WHERE featured=1 ORDER BY RANDOM() LIMIT 3').fetchall()]
    if len(featured) < 3:
        featured = [dict(r) for r in db.execute('SELECT * FROM packages ORDER BY RANDOM() LIMIT 3').fetchall()]
    recent_blogs = [dict(r) for r in db.execute('SELECT * FROM blog_posts ORDER BY created_at DESC LIMIT 3').fetchall()]
    stats = {
        'destinations': db.execute('SELECT COUNT(*) FROM packages').fetchone()[0],
        'travellers':   15000,
        'satisfaction': 98,
    }
    return render_template('index.html', featured=featured, recent_blogs=recent_blogs, stats=stats)

@app.route('/packages')
def packages():
    db = get_db()
    category = request.args.get('category', '')
    q = request.args.get('q', '')
    query = 'SELECT * FROM packages WHERE 1=1'
    params = []
    if category:
        query += ' AND category=?'; params.append(category)
    if q:
        query += ' AND (title LIKE ? OR description LIKE ?)'; params += [f'%{q}%', f'%{q}%']
    pkgs = [dict(r) for r in db.execute(query, params).fetchall()]
    categories = [r['category'] for r in db.execute('SELECT DISTINCT category FROM packages').fetchall()]
    return render_template('packages.html', packages=pkgs, categories=categories,
                           active_cat=category, q=q)

@app.route('/package/<int:pkg_id>')
def package_detail(pkg_id):
    db = get_db()
    pkg = db.execute('SELECT * FROM packages WHERE id=?', (pkg_id,)).fetchone()
    if not pkg:
        flash('Package not found.', 'danger')
        return redirect(url_for('packages'))
    pkg = dict(pkg)
    reviews = db.execute(
        'SELECT r.*,u.name AS user_name FROM reviews r JOIN users u ON r.user_id=u.id WHERE r.package_id=? ORDER BY r.created_at DESC',
        (pkg_id,)).fetchall()
    related = [dict(r) for r in db.execute(
        'SELECT * FROM packages WHERE category=? AND id!=? ORDER BY RANDOM() LIMIT 3',
        (pkg['category'], pkg_id)).fetchall()]
    avg_rating = db.execute('SELECT AVG(rating) FROM reviews WHERE package_id=?', (pkg_id,)).fetchone()[0] or pkg['rating']
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = bool(db.execute('SELECT id FROM wishlist WHERE user_id=? AND package_id=?',
                                      (session['user_id'], pkg_id)).fetchone())
    return render_template('package_detail.html', pkg=pkg, reviews=reviews,
                           related=related, avg_rating=round(avg_rating, 1), in_wishlist=in_wishlist)

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('packages'))
    return redirect(url_for('packages', q=q))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name    = request.form.get('name','').strip()
        email   = request.form.get('email','').strip()
        subject = request.form.get('subject','').strip()
        message = request.form.get('message','').strip()
        if not all([name, email, subject, message]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('contact'))
        db = get_db()
        db.execute("INSERT INTO contacts (name,email,subject,message) VALUES (?,?,?,?)",
                   (name, email, subject, message))
        db.commit()
        flash('Your message has been sent! We will reply within 24 hours.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/blog')
def blog():
    db = get_db()
    posts = [dict(r) for r in db.execute('SELECT * FROM blog_posts ORDER BY created_at DESC').fetchall()]
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    db = get_db()
    post = db.execute('SELECT * FROM blog_posts WHERE slug=?', (slug,)).fetchone()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('blog'))
    others = [dict(r) for r in db.execute('SELECT * FROM blog_posts WHERE slug!=? LIMIT 2', (slug,)).fetchall()]
    return render_template('blog_post.html', post=dict(post), others=others)

# ── AUTH ROUTES ───────────────────────────────────────────────

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session.clear()
            session.update(user_id=user['id'], email=user['email'], name=user['name'], role=user['role'])
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        if not all([name, email, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))
        db = get_db()
        if db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone():
            flash('Email already registered.', 'warning')
            return redirect(url_for('login'))
        db.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                   (name, email, generate_password_hash(password), 'user'))
        db.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ── USER ROUTES ───────────────────────────────────────────────

@app.route('/book', methods=['GET','POST'])
@login_required
def book():
    db = get_db()
    if request.method == 'POST':
        package_id  = request.form.get('package_id')
        travel_date = request.form.get('travel_date')
        travellers  = int(request.form.get('travellers', 1))
        if not package_id or not travel_date:
            flash('All fields are required.', 'danger')
            return redirect(url_for('book'))
        pkg = db.execute('SELECT price FROM packages WHERE id=?', (package_id,)).fetchone()
        total = (pkg['price'] if pkg else 0) * travellers
        db.execute("INSERT INTO bookings (user_id,package_id,travel_date,travellers,total_price) VALUES (?,?,?,?,?)",
                   (session['user_id'], package_id, travel_date, travellers, total))
        db.execute("INSERT INTO logs (action) VALUES (?)",
                   (f"User {session['email']} booked package {package_id}",))
        db.commit()
        flash('Booking confirmed! Check your dashboard for details.', 'success')
        return redirect(url_for('dashboard'))
    pkgs = [dict(r) for r in db.execute('SELECT id,title,price,image_url,duration FROM packages').fetchall()]
    pre_pkg = request.args.get('pkg', '')
    return render_template('booking.html', packages=pkgs, pre_pkg=pre_pkg)

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    bookings = db.execute(
        '''SELECT b.*,p.title AS pkg_title,p.image_url FROM bookings b
           JOIN packages p ON b.package_id=p.id WHERE b.user_id=? ORDER BY b.created_at DESC''',
        (session['user_id'],)).fetchall()
    wishlist = db.execute(
        '''SELECT p.* FROM packages p JOIN wishlist w ON p.id=w.package_id
           WHERE w.user_id=?''', (session['user_id'],)).fetchall()
    reviews = db.execute(
        '''SELECT r.*,p.title AS pkg_title FROM reviews r
           JOIN packages p ON r.package_id=p.id WHERE r.user_id=? ORDER BY r.created_at DESC''',
        (session['user_id'],)).fetchall()
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    return render_template('dashboard.html', bookings=bookings,
                           wishlist=wishlist, reviews=reviews, user=dict(user))

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    db = get_db()
    if request.method == 'POST':
        name    = request.form.get('name','').strip()
        phone   = request.form.get('phone','').strip()
        country = request.form.get('country','').strip()
        db.execute("UPDATE users SET name=?,phone=?,country=? WHERE id=?",
                   (name, phone, country, session['user_id']))
        db.commit()
        session['name'] = name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    user = dict(db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone())
    return render_template('profile.html', user=user)

@app.route('/wishlist/toggle/<int:pkg_id>', methods=['POST'])
@login_required
def wishlist_toggle(pkg_id):
    db = get_db()
    exists = db.execute('SELECT id FROM wishlist WHERE user_id=? AND package_id=?',
                        (session['user_id'], pkg_id)).fetchone()
    if exists:
        db.execute('DELETE FROM wishlist WHERE user_id=? AND package_id=?',
                   (session['user_id'], pkg_id))
        action = 'removed'
    else:
        db.execute('INSERT INTO wishlist (user_id,package_id) VALUES (?,?)',
                   (session['user_id'], pkg_id))
        action = 'added'
    db.commit()
    return jsonify({'status': action})

@app.route('/review/<int:pkg_id>', methods=['POST'])
@login_required
def add_review(pkg_id):
    rating  = int(request.form.get('rating', 5))
    comment = request.form.get('comment','').strip()
    if not comment:
        flash('Please write a review comment.', 'danger')
        return redirect(url_for('package_detail', pkg_id=pkg_id))
    db = get_db()
    existing = db.execute('SELECT id FROM reviews WHERE user_id=? AND package_id=?',
                          (session['user_id'], pkg_id)).fetchone()
    if existing:
        flash('You have already reviewed this package.', 'warning')
        return redirect(url_for('package_detail', pkg_id=pkg_id))
    db.execute("INSERT INTO reviews (user_id,package_id,rating,comment) VALUES (?,?,?,?)",
               (session['user_id'], pkg_id, rating, comment))
    db.commit()
    flash('Review submitted! Thank you.', 'success')
    return redirect(url_for('package_detail', pkg_id=pkg_id))

# ── ADMIN ROUTES ──────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin():
    db = get_db()
    stats = {
        'total_users':    db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_packages': db.execute('SELECT COUNT(*) FROM packages').fetchone()[0],
        'total_bookings': db.execute('SELECT COUNT(*) FROM bookings').fetchone()[0],
        'total_revenue':  db.execute('SELECT COALESCE(SUM(total_price),0) FROM bookings').fetchone()[0],
        'total_contacts': db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0],
        'total_reviews':  db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0],
    }
    users    = db.execute('SELECT id,name,email,role,created_at FROM users ORDER BY created_at DESC').fetchall()
    bookings = db.execute(
        '''SELECT b.*,u.email AS user_email,p.title AS pkg_title
           FROM bookings b JOIN users u ON b.user_id=u.id JOIN packages p ON b.package_id=p.id
           ORDER BY b.created_at DESC''').fetchall()
    packages = db.execute('SELECT * FROM packages ORDER BY created_at DESC').fetchall()
    contacts = db.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    reviews  = db.execute(
        '''SELECT r.*,u.name AS user_name,p.title AS pkg_title
           FROM reviews r JOIN users u ON r.user_id=u.id JOIN packages p ON r.package_id=p.id
           ORDER BY r.created_at DESC''').fetchall()
    logs = db.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20').fetchall()
    return render_template('admin.html', stats=stats, users=users, bookings=bookings,
                           packages=packages, contacts=contacts, reviews=reviews, logs=logs)

@app.route('/admin/package', methods=['POST'])
@admin_required
def admin_add_package():
    d = request.get_json()
    db = get_db()
    db.execute("INSERT INTO packages (title,description,long_description,price,duration,category,image_url,featured) VALUES (?,?,?,?,?,?,?,?)",
               (d['title'],d['description'],d.get('long_description',''),
                float(d['price']),d.get('duration','7 Days'),d.get('category','Beach'),
                d['image_url'], int(d.get('featured',0))))
    db.commit()
    return jsonify({'status':'created'}), 201

@app.route('/admin/package/<int:pid>', methods=['PUT','DELETE'])
@admin_required
def admin_package_crud(pid):
    db = get_db()
    if request.method == 'DELETE':
        db.execute('DELETE FROM packages WHERE id=?', (pid,))
        db.commit()
        return jsonify({'status':'deleted'})
    d = request.get_json()
    db.execute("UPDATE packages SET title=?,description=?,price=?,duration=?,category=?,image_url=?,featured=? WHERE id=?",
               (d['title'],d['description'],float(d['price']),d.get('duration','7 Days'),
                d.get('category','Beach'),d['image_url'],int(d.get('featured',0)),pid))
    db.commit()
    return jsonify({'status':'updated'})

@app.route('/admin/user/<int:uid>', methods=['DELETE'])
@admin_required
def admin_delete_user(uid):
    db = get_db()
    db.execute('DELETE FROM users WHERE id=?', (uid,))
    db.commit()
    return jsonify({'status':'deleted'})

@app.route('/admin/booking/<int:bid>', methods=['DELETE'])
@admin_required
def admin_delete_booking(bid):
    db = get_db()
    db.execute('DELETE FROM bookings WHERE id=?', (bid,))
    db.commit()
    return jsonify({'status':'deleted'})

@app.route('/admin/review/<int:rid>', methods=['DELETE'])
@admin_required
def admin_delete_review(rid):
    db = get_db()
    db.execute('DELETE FROM reviews WHERE id=?', (rid,))
    db.commit()
    return jsonify({'status':'deleted'})

# ── API ENDPOINTS ─────────────────────────────────────────────

@app.route('/api/packages')
def api_packages():
    db = get_db()
    return jsonify([dict(r) for r in db.execute('SELECT * FROM packages').fetchall()])

@app.route('/api/packages/<int:pid>')
def api_package(pid):
    db = get_db()
    r = db.execute('SELECT * FROM packages WHERE id=?', (pid,)).fetchone()
    return jsonify(dict(r)) if r else ('', 404)

@app.route('/api/bookings')
@login_required
def api_bookings():
    db = get_db()
    rows = db.execute(
        'SELECT b.*,p.title FROM bookings b JOIN packages p ON b.package_id=p.id WHERE b.user_id=?',
        (session['user_id'],)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/book', methods=['POST'])
@login_required
def api_book():
    d = request.get_json() or {}
    if not d.get('package_id') or not d.get('travel_date'):
        return jsonify({'error':'missing fields'}), 400
    db = get_db()
    pkg = db.execute('SELECT price FROM packages WHERE id=?', (d['package_id'],)).fetchone()
    total = (pkg['price'] if pkg else 0) * int(d.get('travellers',1))
    db.execute("INSERT INTO bookings (user_id,package_id,travel_date,travellers,total_price) VALUES (?,?,?,?,?)",
               (session['user_id'],d['package_id'],d['travel_date'],d.get('travellers',1),total))
    db.commit()
    return jsonify({'status':'booked'}), 201

@app.route('/api/search')
def api_search():
    q = request.args.get('q','')
    db = get_db()
    rows = db.execute('SELECT id,title,image_url,price FROM packages WHERE title LIKE ? LIMIT 5',
                      (f'%{q}%',)).fetchall()
    return jsonify([dict(r) for r in rows])

# ── STARTUP ───────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        tbl = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='packages'").fetchone()
        if not tbl:
            init_db()
            print('Database initialised.')
        else:
            print('Database ready.')
    app.run(debug=True, port=5000)
