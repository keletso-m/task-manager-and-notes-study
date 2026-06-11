"""
Run this once before starting the app for the first time.
Creates db/focus.db with both tables.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "focus.db")


def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            task_type   TEXT DEFAULT 'daily',
            completed   BOOLEAN DEFAULT 0,
            due_date    DATE,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            body       TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.commit()
    db.close()
    print(" Database initialised at db/focus.db")
    print("   Tables: tasks, notes")


if __name__ == "__main__":
    init()