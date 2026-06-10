from flask import Blueprint, request, jsonify
from .database import get_db
from .authentication import token_required

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/api/tasks", methods=["GET"])
@token_required
def get_tasks(current_user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (current_user_id,)
    )

    tasks = cursor.fetchall()
    conn.close()

    return jsonify({
        "tasks": [dict(task) for task in tasks]
    }), 200


@tasks_bp.route("/api/tasks", methods=["POST"])
@token_required
def create_task(current_user_id):
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"message": "Title required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
        (current_user_id, data["title"], data.get("description", ""))
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task created"}), 201
