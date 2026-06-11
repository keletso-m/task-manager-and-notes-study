"""
Focus — Flask backend
No auth. Runs locally on localhost:5000.
"""

import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = "db/focus.db"


# Database helpers


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
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



# Health


@app.route("/health")
def health():
    return jsonify({"status": "ok"})



# Tasks


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    db = get_db()
    task_type = request.args.get("type")          # ?type=daily or ?type=goal
    completed = request.args.get("completed")     # ?completed=0 or ?completed=1

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if task_type:
        query += " AND task_type = ?"
        params.append(task_type)
    if completed is not None:
        query += " AND completed = ?"
        params.append(int(completed))

    query += " ORDER BY due_date ASC, created_at DESC"
    rows = db.execute(query, params).fetchall()

    tasks = []
    for row in rows:
        tasks.append({
            "id":          row["id"],
            "title":       row["title"],
            "description": row["description"],
            "task_type":   row["task_type"],
            "completed":   bool(row["completed"]),
            "due_date":    row["due_date"],
            "created_at":  row["created_at"],
        })
    return jsonify({"tasks": tasks})


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    description = data.get("description", "")
    task_type   = data.get("task_type", "daily")   # 'daily' or 'goal'
    due_date    = data.get("due_date")              # ISO date string or None

    db = get_db()
    cursor = db.execute(
        "INSERT INTO tasks (title, description, task_type, due_date) VALUES (?, ?, ?, ?)",
        (title, description, task_type, due_date)
    )
    db.commit()
    return jsonify({"message": "Task created", "task_id": cursor.lastrowid}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    db = get_db()

    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    title       = data.get("title",       task["title"])
    description = data.get("description", task["description"])
    task_type   = data.get("task_type",   task["task_type"])
    completed   = data.get("completed",   task["completed"])
    due_date    = data.get("due_date",    task["due_date"])

    db.execute(
        """UPDATE tasks
           SET title = ?, description = ?, task_type = ?,
               completed = ?, due_date = ?
           WHERE id = ?""",
        (title, description, task_type, int(completed), due_date, task_id)
    )
    db.commit()
    return jsonify({"message": "Task updated"})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    task = db.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return jsonify({"message": "Task deleted"})



# Notes


@app.route("/api/notes", methods=["GET"])
def get_notes():
    db = get_db()
    search = request.args.get("q", "").strip()   # ?q=search term

    if search:
        rows = db.execute(
            "SELECT * FROM notes WHERE title LIKE ? ORDER BY updated_at DESC",
            (f"%{search}%",)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM notes ORDER BY updated_at DESC"
        ).fetchall()

    notes = []
    for row in rows:
        notes.append({
            "id":         row["id"],
            "title":      row["title"],
            "body":       row["body"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    return jsonify({"notes": notes})


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    db = get_db()
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not row:
        return jsonify({"error": "Note not found"}), 404
    return jsonify({
        "id":         row["id"],
        "title":      row["title"],
        "body":       row["body"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    })


@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    body = data.get("body", "")
    db = get_db()
    cursor = db.execute(
        "INSERT INTO notes (title, body) VALUES (?, ?)",
        (title, body)
    )
    db.commit()
    return jsonify({"message": "Note created", "note_id": cursor.lastrowid}), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    db = get_db()

    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    title = data.get("title", note["title"])
    body  = data.get("body",  note["body"])
    now   = datetime.utcnow().isoformat()

    db.execute(
        "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
        (title, body, now, note_id)
    )
    db.commit()
    return jsonify({"message": "Note updated"})


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db = get_db()
    note = db.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return jsonify({"message": "Note deleted"})



# Run


if __name__ == "__main__":
    init_db()
    print("Focus backend running on http://localhost:5000")
    app.run(debug=True, port=5000)