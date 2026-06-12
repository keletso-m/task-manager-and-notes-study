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



if __name__ == "__main__":
    app = FocusApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()