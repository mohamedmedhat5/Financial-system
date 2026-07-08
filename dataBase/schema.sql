CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY,
    name             TEXT        NOT NULL,
    email            TEXT        UNIQUE NOT NULL,
    password_hash    TEXT        NOT NULL,
    age              INTEGER,
    country          TEXT,
    occupation_level TEXT,
    salary           REAL,
    created_at       TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date        TEXT        NOT NULL,
    category    TEXT,
    note        TEXT,
    amount      REAL        NOT NULL CHECK (amount >= 0),
    type        TEXT        NOT NULL CHECK (type IN ('income', 'expense')),
    currency    TEXT        DEFAULT 'USD',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions (user_id, date);
