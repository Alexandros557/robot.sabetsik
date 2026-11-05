import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent / "robocareer.db"

@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def init_db():
    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                stage TEXT,
                interests TEXT,
                preferred_tasks TEXT,
                experience TEXT,
                recommended_career TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

def save_user(user_id, username=None, first_name=None):
    with get_connection() as con:
        con.execute("""
            INSERT INTO users(user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name
        """, (user_id, username, first_name))

def save_profile(user_id, stage, interests, preferred_tasks, experience, career):
    with get_connection() as con:
        con.execute("""
            INSERT INTO profiles(
                user_id, stage, interests, preferred_tasks, experience,
                recommended_career, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                stage=excluded.stage,
                interests=excluded.interests,
                preferred_tasks=excluded.preferred_tasks,
                experience=excluded.experience,
                recommended_career=excluded.recommended_career,
                updated_at=CURRENT_TIMESTAMP
        """, (user_id, stage, interests, preferred_tasks, experience, career))

def get_profile(user_id):
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

def get_user_count():
    with get_connection() as con:
        row = con.execute("SELECT COUNT(*) AS total FROM users").fetchone()
        return row["total"]
