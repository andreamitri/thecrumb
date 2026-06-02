import sqlite3, os, sys

BASE_DIR    = os.path.dirname(__file__)
DATA_DIR    = os.path.join(BASE_DIR, "data")
DB_PATH     = os.path.join(DATA_DIR, "blog.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def migrate():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.isolation_level = None
    conn.executescript(sql)
    conn.close()
    print(f"Database created: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    for table in ["posts", "tags", "post_tags", "comments"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
    conn.close()

if __name__ == "__main__":
    migrate()