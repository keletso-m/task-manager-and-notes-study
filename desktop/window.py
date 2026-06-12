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
        


if __name__ == "__main__":
    app = FocusApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()