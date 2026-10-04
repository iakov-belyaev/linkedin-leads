import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                linkedin_url TEXT UNIQUE,
                title_snippet TEXT,
                body_snippet TEXT,
                target_role TEXT,
                status TEXT DEFAULT 'New',
                ai_draft_pitch TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def insert_lead(linkedin_url, title_snippet, body_snippet, target_role="General"):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO leads (linkedin_url, title_snippet, body_snippet, target_role)
                VALUES (?, ?, ?, ?)
            ''', (linkedin_url, title_snippet, body_snippet, target_role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Skip duplicate URLs

def get_next_new_lead():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, linkedin_url, title_snippet, body_snippet, target_role
            FROM leads
            WHERE status = 'New'
            ORDER BY id ASC
            LIMIT 1
        ''')
        return cursor.fetchone()

def update_lead_status(lead_id, status, ai_draft_pitch=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if ai_draft_pitch:
            cursor.execute('''
                UPDATE leads
                SET status = ?, ai_draft_pitch = ?
                WHERE id = ?
            ''', (status, ai_draft_pitch, lead_id))
        else:
            cursor.execute('''
                UPDATE leads
                SET status = ?
                WHERE id = ?
            ''', (status, lead_id))
        conn.commit()

def get_remaining_count():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'New'")
        return cursor.fetchone()[0]