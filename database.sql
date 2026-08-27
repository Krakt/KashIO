-- Table for payment methods
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- 'Espèces', 'Carte', 'Twint', 'Bon cadeau', etc.
    is_active BOOLEAN DEFAULT 1
);

-- Table for closures (daily summaries)
CREATE TABLE IF NOT EXISTS closures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    closure_date TEXT UNIQUE NOT NULL, -- Format 'YYYY-MM-DD'
    is_email_sent BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for tickets (sales)
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    closure_id INTEGER NOT NULL,
    is_evening BOOLEAN DEFAULT 0,       -- 0 = Launch, 1 = Evening
    location_id INTEGER DEFAULT 1,     -- 1 = Eatin, 2 = Takeaway, 3 = Delivery
    method TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (closure_id) REFERENCES closures(id) ON DELETE CASCADE
);

-- Table for reductions (discounts)
CREATE TABLE IF NOT EXISTS reductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    closure_id INTEGER NOT NULL,
    count INTEGER NOT NULL,
    method TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (closure_id) REFERENCES closures(id) ON DELETE CASCADE
);

-- Table for stored shops / vendors
CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

-- Table for expenses
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER NOT NULL,
    category_code TEXT NOT NULL, -- Storing the localization code (e.g., 'cat_food')
    amount REAL NOT NULL,
    paid_in_cash BOOLEAN DEFAULT 1, -- True if payed in cash
    FOREIGN KEY (closure_id) REFERENCES closures(id) ON DELETE CASCADE,
    FOREIGN KEY (shop_id) REFERENCES shops(id)
);

CREATE TABLE IF NOT EXISTS db_version (
    version INTEGER PRIMARY KEY
);
INSERT OR IGNORE INTO db_version (version) VALUES (1); -- Version initiale

-- Insert default payment methods
INSERT OR IGNORE INTO payment_methods (name) VALUES ('Espèces'), ('Carte'), ('Recka'), ('Twint'), ('Autre');