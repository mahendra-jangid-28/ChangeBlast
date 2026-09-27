"""
Database migration scripts for the e-commerce platform.
"""

# Migration 001 — initial schema
MIGRATION_001 = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_id INTEGER NOT NULL REFERENCES orders(id),
    amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    stripe_payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Migration 002 — add indexes
MIGRATION_002 = """
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
"""

# PENDING MIGRATION — if User.id changes to UUID:
# Migration 003 — change users.id from INTEGER to UUID (TEXT)
MIGRATION_003_PENDING = """
-- Step 1: Add uuid column
ALTER TABLE users ADD COLUMN uuid TEXT;

-- Step 2: Populate UUIDs
UPDATE users SET uuid = lower(hex(randomblob(4))) || '-' ||
    lower(hex(randomblob(2))) || '-4' ||
    lower(hex(randomblob(2)))[1:3] || ...;

-- Step 3: Update all FK columns in dependent tables
ALTER TABLE orders ADD COLUMN user_uuid TEXT;
UPDATE orders SET user_uuid = (SELECT uuid FROM users WHERE users.id = orders.user_id);

ALTER TABLE payments ADD COLUMN user_uuid TEXT;
UPDATE payments SET user_uuid = (SELECT uuid FROM users WHERE users.id = payments.user_id);

ALTER TABLE user_sessions ADD COLUMN user_uuid TEXT;
UPDATE user_sessions SET user_uuid = (SELECT uuid FROM users WHERE users.id = user_sessions.user_id);

-- Step 4: Drop old integer columns (requires table rebuild in SQLite)
"""
