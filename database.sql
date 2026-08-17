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
    wording TEXT,
    is_evening BOOLEAN DEFAULT 0,
    is_takeaway BOOLEAN DEFAULT 0,
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

-- Table for expenses
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    closure_id INTEGER NOT NULL,
    wording TEXT NOT NULL, -- ex: "3x Salades", "Essence livreur"
    amount REAL NOT NULL,
    paid_in_cash BOOLEAN DEFAULT 1, -- True si payé directement avec le cash du tiroir
    FOREIGN KEY (closure_id) REFERENCES closures(id) ON DELETE CASCADE
);

-- Insert default payment methods
INSERT OR IGNORE INTO payment_methods (name) VALUES ('Espèces'), ('Carte'), ('Recka'), ('Twint'), ('Autre');