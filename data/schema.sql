CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS niches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    niche_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    FOREIGN KEY (niche_id) REFERENCES niches (id)
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    niche_id INTEGER,
    confidence REAL,
    feedback TEXT, -- 'correct', 'incorrect', or corrected niche name
    labels TEXT, -- JSON string of detected labels
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (niche_id) REFERENCES niches (id)
);
