DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS packages;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS blog_posts;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user','admin')),
    phone TEXT,
    country TEXT,
    avatar TEXT DEFAULT 'default.jpg',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    long_description TEXT,
    price REAL NOT NULL,
    duration TEXT DEFAULT '7 days',
    category TEXT DEFAULT 'Beach',
    image_url TEXT NOT NULL,
    rating REAL DEFAULT 4.5,
    featured INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    travel_date TEXT NOT NULL,
    travellers INTEGER DEFAULT 1,
    total_price REAL,
    status TEXT DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
);

CREATE TABLE wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    UNIQUE(user_id, package_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    replied INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    excerpt TEXT NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT NOT NULL,
    author TEXT DEFAULT 'Wanderlust Team',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed packages
INSERT INTO packages (title,description,long_description,price,duration,category,image_url,rating,featured) VALUES
('Maldives Getaway','7-night luxury overwater bungalow stay.','Experience paradise in the Maldives with crystal-clear lagoons, vibrant coral reefs, and world-class dining. Your private overwater bungalow comes with a glass floor, direct ocean access, and butler service. Includes snorkeling, sunset cruise, and spa treatments.',2999.99,'7 Days','Beach','maldives.jpg',4.9,1),
('Swiss Alps Adventure','Ski resort package with guided tours.','Conquer the Swiss Alps with expert ski guides, cozy mountain lodges, and breathtaking panoramic views. Package includes lift passes, equipment rental, après-ski activities, fondue dinner, and a scenic train ride through the Jungfrau region.',1999.99,'10 Days','Adventure','switzerland.jpg',4.7,1),
('Paris Romance','Romantic 5-day city break.','Fall in love with the City of Light. Enjoy a Seine river cruise, private Eiffel Tower visit at sunset, wine tasting in Montmartre, a cooking class, and a day trip to the Palace of Versailles. Perfect for couples and honeymoons.',1499.99,'5 Days','City','paris.jpg',4.8,1),
('Dubai Luxury','5-day desert and city experience.','Experience the ultimate luxury in Dubai — desert safaris, Burj Khalifa observation deck, private yacht cruise along the marina, gold souk shopping tour, and helicopter ride over the Palm Jumeirah.',1799.99,'5 Days','Luxury','dubai.jpg',4.6,0),
('Japan Explorer','10-day cultural tour across Japan.','Immerse yourself in Japan from ancient Kyoto temples to futuristic Tokyo streets. Includes bullet train pass, traditional ryokan stays, tea ceremony, Mount Fuji day trip, and street food tours through Osaka.',2599.99,'10 Days','Culture','japan.jpg',5.0,0);

-- Seed blog posts
INSERT INTO blog_posts (title,slug,excerpt,content,image_url,author) VALUES
('Top 10 Hidden Beaches in the Maldives','top-10-maldives-beaches','Discover secluded paradises away from the crowds in the Maldives archipelago.','The Maldives is home to over 1,200 islands, yet most tourists visit only a handful. We''ve curated the most breathtaking hidden beaches that will leave you speechless. From the bioluminescent shores of Vaadhoo to the untouched Fulhadhoo lagoon, these spots are pure magic.','maldives.jpg','Sarah Johnson'),
('A Foodies Guide to Japan Street Food','japan-street-food-guide','From takoyaki to ramen, Japan''s street food scene is an explosion of flavors.','Japan offers one of the world''s most exciting street food cultures. Osaka is considered the food capital, with Dotonbori street lined with izakayas, ramen shops, and the famous takoyaki stalls. Tokyo''s Tsukiji outer market is a must-visit for sushi lovers.','japan.jpg','Marco Rossi'),
('Planning the Perfect Swiss Alps Ski Trip','swiss-alps-ski-guide','Everything you need to know before hitting the slopes in Switzerland.','Switzerland boasts some of the finest ski resorts in the world. Zermatt, St. Moritz, and Verbier are legendary among ski enthusiasts. We break down the best slopes for beginners and experts alike, the finest mountain restaurants, and insider tips for avoiding the crowds.','switzerland.jpg','Wanderlust Team');

-- Seed sample reviews
INSERT INTO reviews (user_id,package_id,rating,comment) VALUES
(1,1,5,'Absolutely magical! The overwater bungalow was a dream. Will definitely return!'),
(1,3,5,'Paris exceeded every expectation. The Eiffel Tower at night was unforgettable.');
