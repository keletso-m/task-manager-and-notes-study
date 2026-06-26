# Focus Personal Study & Task Manager

> A personal desktop productivity app built on top of a Flask + SQLite backend.  
> No auth. No cloud. Just yours.

Built by Keletso Monyamane · MIT License · Python 3.11+ · Flask · SQLite · CustomTkinter

---

## What Is Focus?

Focus is a desktop app for Linux that replaces scattered paper notes and forgotten tasks with one place to think, plan, and study. It lives in your system tray, fires desktop notifications, and keeps everything stored locally on your machine.

It started as a Task Manager API and was rebuilt into a personal tool the REST backend is still there under the hood, but the frontend is now a native desktop app.

---

## Features

| Feature | Status |
|---|---|
| Task checklist — tick off and done | Done |
| Long-term goals (with target dates) | Done |
| Day-to-day tasks | Done |
| Future-dated tasks and reminders | Done |
| Notes with headings (like a mini doc) | Done |
| Pomodoro timer | Done |
| Desktop notifications (Linux native) | Done |
| System tray icon | Done |
| SQLite — all data stays on your machine | Done |
| Recurring tasks | Planned |
| Colour-coded categories / tags | Planned |
| Export notes to PDF | Planned |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.0 · Python 3.11+ |
| Database | SQLite (local, no setup needed) |
| Desktop UI | CustomTkinter |
| System Tray | pystray + Pillow |
| Notifications | plyer + `notify-send` (Linux) |
| CI/CD | GitHub Actions |


---

## Quickstart

### 1. Clone and set up

```bash
git clone https://github.com/keletso-m/task-manager-api.git
cd task-manager-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialise the database

```bash
python scripts/init_db.py
```

### 3. Start the backend

```bash
python app/app.py
```

Runs on `http://localhost:5000` — the desktop app talks to this automatically.

### 4. Launch the desktop app

```bash
python desktop/main.py
```

The app opens and an icon appears in your system tray. You can close the window and reopen it from the tray anytime.

---

## How It Works

### Tasks

Tasks come in two types:

- **Day-to-day** — things to get done today or this week
- **Long-term goals** — bigger targets with a future due date

Both types can be ticked off. Completed tasks move to a "Done" section so you still see the progress.

You can set any task to a future date and Focus will send you a desktop notification on that day as a reminder.

### Notes

Notes support headings so you can structure your thinking like a lightweight doc. Each note has a title and free-form body. Good for:
- Study notes per subject
- Summaries and revision
- Anything you'd normally write on paper

### Pomodoro Timer

A built-in custom Pomodoro timer. When a session ends, a desktop notification fires so you don't have to watch the clock.

You can customise work and break durations in the settings panel.

### Notifications

Focus uses Linux native notifications (`notify-send` + `plyer`) to send alerts for:
- Pomodoro session end / break end
- Task due today
- Future-dated task reminders

---

## Project Structure

```
focus/
├── app/
│   ├── app.py                  # Flask backend (no auth)
│   └── routes/
│       ├── tasks.py            # GET, POST, PUT, DELETE /api/tasks
│       └── notes.py            # GET, POST, PUT, DELETE /api/notes
├── desktop/
│   ├── main.py                 # Entry point — starts backend + launches window
│   ├── window.py               # Main app window (Tasks, Notes, Pomodoro tabs)
│   ├── tray.py                 # System tray icon + right-click menu
│   └── notifier.py             # Desktop notification helper
├── scripts/
│   └── init_db.py              # Creates tables on first run
├── tests/
│   └── test_app.py             # Unit tests
├── requirements.txt
└── README.md
```

---

## API (Internal)

The Flask backend is what stores and serves all the data. You don't need to touch it directly the desktop app handles everything but it's there if you want to extend it.

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/tasks | Get all tasks |
| POST | /api/tasks | Create a task |
| PUT | /api/tasks/{id} | Update / tick off a task |
| DELETE | /api/tasks/{id} | Delete a task |
| GET | /api/notes | Get all notes |
| POST | /api/notes | Create a note |
| PUT | /api/notes/{id} | Update a note |
| DELETE | /api/notes/{id} | Delete a note |
| GET | /health | Liveness check |

---

## Database Schema

```sql
-- Tasks
CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    task_type   TEXT DEFAULT 'daily',   -- 'daily' or 'goal'
    completed   BOOLEAN DEFAULT 0,
    due_date    DATE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Notes
CREATE TABLE notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    body       TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Roadmap

- [ ] Recurring tasks (daily / weekly)
- [ ] Subject tags for notes
- [ ] Export notes to PDF
- [ ] Colour themes
- [ ] Search across tasks and notes

---

## License

MIT — use it, break it, make it yours.

Built by Keletso Monyamane — [github.com/keletso-m](https://github.com/keletso-m)
