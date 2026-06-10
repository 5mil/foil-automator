-- foil-automator schema
CREATE TABLE IF NOT EXISTS requests (
    id            INTEGER PRIMARY KEY,
    agency        TEXT NOT NULL,
    submitted     DATE NOT NULL,
    ack_deadline  DATE NOT NULL,
    prod_deadline DATE NOT NULL,
    appeal_by     DATE NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',
    portal_url    TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_prod_deadline ON requests(prod_deadline);
