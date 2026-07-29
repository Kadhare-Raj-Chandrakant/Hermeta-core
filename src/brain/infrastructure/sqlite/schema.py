from brain.infrastructure.sqlite.connection import SQLiteConnection

SCHEMA_VERSION = 3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS identities (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
    identity_id TEXT NOT NULL,
    version_id TEXT UNIQUE NOT NULL,
    version_number INTEGER NOT NULL,
    knowledge_type TEXT NOT NULL,
    title TEXT NOT NULL,
    understanding TEXT NOT NULL,
    confidence REAL NOT NULL,
    lifecycle_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (identity_id) REFERENCES identities(id),
    UNIQUE(identity_id, version_number)
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identity_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    source TEXT NOT NULL,
    reference TEXT NOT NULL,
    FOREIGN KEY (identity_id, version_number)
        REFERENCES versions(identity_id, version_number)
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identity_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    FOREIGN KEY (identity_id, version_number)
        REFERENCES versions(identity_id, version_number)
);

CREATE TABLE IF NOT EXISTS transitions (
    id TEXT PRIMARY KEY,
    from_version_id TEXT NOT NULL,
    to_version_id TEXT NOT NULL,
    transition_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    confidence REAL NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conflicts (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    resolution TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS conflict_versions (
    conflict_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    FOREIGN KEY (conflict_id) REFERENCES conflicts(id),
    UNIQUE(conflict_id, version_id)
);
"""

MIGRATION_SQL = """
ALTER TABLE versions ADD COLUMN version_id TEXT;
"""


def initialize_schema(conn: SQLiteConnection) -> None:
    conn.connect().executescript(SCHEMA_SQL)

    row = conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()
    elif row["version"] < SCHEMA_VERSION:
        for statement in MIGRATION_SQL.strip().split(";"):
            statement = statement.strip()
            if statement:
                try:
                    conn.execute(statement)
                except Exception:
                    pass
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()
