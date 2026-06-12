"""
Focus — Main app window
Three tabs: Tasks · Notes · Pomodoro
"""

import customtkinter as ctk
import requests
import threading
from datetime import date, datetime
from notifier import notify

API = "http://localhost:5000/api"

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK_BG    = "#1a1a2e"
PANEL_BG   = "#16213e"
CARD_BG    = "#0f3460"
ACCENT     = "#e94560"
TEXT_MAIN  = "#eaeaea"
TEXT_DIM   = "#888888"
TICK_GREEN = "#4ecca3"



# Helpers


def api_get(path, params=None):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=5)
        return r.json()
    except Exception as e:
        print(f"GET {path} failed: {e}")
        return None


def api_post(path, data):
    try:
        r = requests.post(f"{API}{path}", json=data, timeout=5)
        return r.json()
    except Exception as e:
        print(f"POST {path} failed: {e}")
        return None


def api_put(path, data):
    try:
        r = requests.put(f"{API}{path}", json=data, timeout=5)
        return r.json()
    except Exception as e:
        print(f"PUT {path} failed: {e}")
        return None


def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=5)
        return r.json()
    except Exception as e:
        print(f"DELETE {path} failed: {e}")
        return None
    
# task Tab 

class TasksTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=DARK_BG)
        self.selected_type = ctk.StringVar(value="daily")
        self._build()
        self.load_tasks()
 
    def _build(self):
        # Top bar — toggle daily / goals
        top = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10)
        top.pack(fill="x", padx=16, pady=(16, 8))
 
        ctk.CTkLabel(top, text="Tasks", font=("Helvetica", 20, "bold"),
                     text_color=TEXT_MAIN).pack(side="left", padx=16, pady=12)
 
        toggle = ctk.CTkSegmentedButton(
            top,
            values=["Today", "Goals"],
            variable=self.selected_type,
            command=self._on_toggle,
            fg_color=CARD_BG,
            selected_color=ACCENT,
            selected_hover_color=ACCENT,
            text_color=TEXT_MAIN,
        )
        toggle.pack(side="right", padx=16, pady=12)
        toggle.set("Today")
 
        # Add task row
        add_row = ctk.CTkFrame(self, fg_color="transparent")
        add_row.pack(fill="x", padx=16, pady=(0, 8))
 
        self.new_title = ctk.CTkEntry(
            add_row, placeholder_text="New task...",
            fg_color=PANEL_BG, border_color=CARD_BG,
            text_color=TEXT_MAIN, height=38
        )
        self.new_title.pack(side="left", fill="x", expand=True, padx=(0, 8))
 
        self.due_entry = ctk.CTkEntry(
            add_row, placeholder_text="Due date (YYYY-MM-DD)",
            fg_color=PANEL_BG, border_color=CARD_BG,
            text_color=TEXT_MAIN, height=38, width=180
        )
        self.due_entry.pack(side="left", padx=(0, 8))
 
        ctk.CTkButton(
            add_row, text="Add", width=70, height=38,
            fg_color=ACCENT, hover_color="#c73652",
            command=self.add_task
        ).pack(side="left")
 
        # Scrollable task list
        self.task_list = ctk.CTkScrollableFrame(
            self, fg_color=PANEL_BG, corner_radius=10
        )
        self.task_list.pack(fill="both", expand=True, padx=16, pady=(0, 16))
 
    def _on_toggle(self, value):
        self.load_tasks()
 
    def load_tasks(self):
        for w in self.task_list.winfo_children():
            w.destroy()
 
        task_type = "daily" if self.selected_type.get() == "Today" else "goal"
        data = api_get("/tasks", params={"type": task_type, "completed": 0})
        done = api_get("/tasks", params={"type": task_type, "completed": 1})
 
        if data:
            for t in data["tasks"]:
                self._task_row(t, done=False)
 
        if done and done["tasks"]:
            ctk.CTkLabel(
                self.task_list, text="Completed",
                font=("Helvetica", 12), text_color=TEXT_DIM
            ).pack(anchor="w", padx=12, pady=(16, 4))
            for t in done["tasks"]:
                self._task_row(t, done=True)
 
    def _task_row(self, task, done=False):
        row = ctk.CTkFrame(self.task_list, fg_color=CARD_BG, corner_radius=8)
        row.pack(fill="x", padx=8, pady=4)
 
        # Checkbox
        var = ctk.BooleanVar(value=done)
        cb = ctk.CTkCheckBox(
            row, text="", variable=var, width=32,
            fg_color=TICK_GREEN, hover_color=TICK_GREEN,
            border_color=TEXT_DIM,
            command=lambda t=task, v=var: self._toggle(t, v)
        )
        cb.pack(side="left", padx=(12, 4), pady=10)
 
        # Title + due date
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=8)
 
        title_color = TEXT_DIM if done else TEXT_MAIN
        ctk.CTkLabel(
            info, text=task["title"],
            font=("Helvetica", 14), text_color=title_color, anchor="w"
        ).pack(anchor="w")
 
        if task.get("due_date"):
            ctk.CTkLabel(
                info, text=f"Due {task['due_date']}",
                font=("Helvetica", 11), text_color=TEXT_DIM, anchor="w"
            ).pack(anchor="w")
 
        # Delete button
        ctk.CTkButton(
            row, text="✕", width=28, height=28,
            fg_color="transparent", hover_color=PANEL_BG,
            text_color=TEXT_DIM,
            command=lambda t=task: self._delete(t)
        ).pack(side="right", padx=8)
 
    def add_task(self):
        title = self.new_title.get().strip()
        if not title:
            return
        due = self.due_entry.get().strip() or None
        task_type = "daily" if self.selected_type.get() == "Today" else "goal"
        api_post("/tasks", {"title": title, "task_type": task_type, "due_date": due})
        self.new_title.delete(0, "end")
        self.due_entry.delete(0, "end")
        self.load_tasks()
 
    def _toggle(self, task, var):
        api_put(f"/tasks/{task['id']}", {"completed": var.get()})
        self.after(300, self.load_tasks)
 
    def _delete(self, task):
        api_delete(f"/tasks/{task['id']}")
        self.load_tasks()

# notes Tab 
class NotesTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=DARK_BG)
        self.current_note_id = None
        self._autosave_job = None
        self._build()
        self.load_notes()
 
    def _build(self):
        # Left panel — note list
        left = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10, width=220)
        left.pack(side="left", fill="y", padx=(16, 8), pady=16)
        left.pack_propagate(False)
 
        ctk.CTkLabel(
            left, text="Notes", font=("Helvetica", 18, "bold"), text_color=TEXT_MAIN
        ).pack(padx=12, pady=(12, 8), anchor="w")
 
        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load_notes())
        ctk.CTkEntry(
            left, placeholder_text="Search...",
            textvariable=self.search_var,
            fg_color=CARD_BG, border_color=CARD_BG,
            text_color=TEXT_MAIN, height=34
        ).pack(fill="x", padx=12, pady=(0, 8))
 
        # New note button
        ctk.CTkButton(
            left, text="+ New note", height=34,
            fg_color=ACCENT, hover_color="#c73652",
            command=self.new_note
        ).pack(fill="x", padx=12, pady=(0, 8))
 
        # Note list
        self.note_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.note_list.pack(fill="both", expand=True, padx=4, pady=(0, 8))
 
        # Right panel — editor
        right = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10)
        right.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=16)
 
        # Title input
        self.note_title = ctk.CTkEntry(
            right, placeholder_text="Note title...",
            fg_color=CARD_BG, border_color=CARD_BG,
            text_color=TEXT_MAIN, font=("Helvetica", 16, "bold"), height=42
        )
        self.note_title.pack(fill="x", padx=16, pady=(16, 8))
        self.note_title.bind("<KeyRelease>", self._on_edit)
 
        # Heading hint
        ctk.CTkLabel(
            right,
            text="Tip: use # Heading  ## Sub heading  ### Smaller heading",
            font=("Helvetica", 11), text_color=TEXT_DIM
        ).pack(anchor="w", padx=16, pady=(0, 4))
 
        # Body editor
        self.note_body = ctk.CTkTextbox(
            right, fg_color=CARD_BG, text_color=TEXT_MAIN,
            font=("Helvetica", 13), wrap="word",
            border_width=0, corner_radius=8
        )
        self.note_body.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.note_body.bind("<KeyRelease>", self._on_edit)
 
        # Status bar
        self.status_label = ctk.CTkLabel(
            right, text="", font=("Helvetica", 11), text_color=TEXT_DIM
        )
        self.status_label.pack(anchor="e", padx=16, pady=(0, 12))
 
        # Delete button
        ctk.CTkButton(
            right, text="Delete note", width=110, height=30,
            fg_color="transparent", hover_color=PANEL_BG,
            text_color=TEXT_DIM, border_width=1, border_color=TEXT_DIM,
            command=self.delete_note
        ).pack(anchor="e", padx=16, pady=(0, 12))
 
    def load_notes(self):
        for w in self.note_list.winfo_children():
            w.destroy()
 
        q = self.search_var.get().strip()
        data = api_get("/notes", params={"q": q} if q else None)
        if not data:
            return
 
        for note in data["notes"]:
            self._note_item(note)
 
    def _note_item(self, note):
        is_active = note["id"] == self.current_note_id
        btn = ctk.CTkButton(
            self.note_list,
            text=note["title"],
            anchor="w",
            height=36,
            fg_color=ACCENT if is_active else "transparent",
            hover_color=CARD_BG,
            text_color=TEXT_MAIN,
            font=("Helvetica", 13),
            command=lambda n=note: self.open_note(n["id"])
        )
        btn.pack(fill="x", pady=2)
 
    def open_note(self, note_id):
        data = api_get(f"/notes/{note_id}")
        if not data:
            return
        self.current_note_id = note_id
        self.note_title.delete(0, "end")
        self.note_title.insert(0, data["title"])
        self.note_body.delete("1.0", "end")
        self.note_body.insert("1.0", data["body"] or "")
        self.status_label.configure(text="Saved")
        self.load_notes()
 
    def new_note(self):
        result = api_post("/notes", {"title": "Untitled", "body": ""})
        if result and "note_id" in result:
            self.load_notes()
            self.open_note(result["note_id"])
 
    def _on_edit(self, event=None):
        # Debounce — save 1.5s after the user stops typing
        if self._autosave_job:
            self.after_cancel(self._autosave_job)
        self._autosave_job = self.after(1500, self._autosave)
        self.status_label.configure(text="Unsaved...")
 
    def _autosave(self):
        if not self.current_note_id:
            return
        title = self.note_title.get().strip() or "Untitled"
        body  = self.note_body.get("1.0", "end").strip()
        api_put(f"/notes/{self.current_note_id}", {"title": title, "body": body})
        self.status_label.configure(text=f"Saved · {datetime.now().strftime('%H:%M')}")
        self.load_notes()
 
    def delete_note(self):
        if not self.current_note_id:
            return
        api_delete(f"/notes/{self.current_note_id}")
        self.current_note_id = None
        self.note_title.delete(0, "end")
        self.note_body.delete("1.0", "end")
        self.status_label.configure(text="")
        self.load_notes()
 

if __name__ == "__main__":
    app = FocusApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()