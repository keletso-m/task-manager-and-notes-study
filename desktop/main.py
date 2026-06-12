"""
main.py — Focus entry point
Run this: python desktop/main.py

1. Starts the Flask backend in a background thread
2. Waits for it to be ready
3. Opens the desktop window
4. Starts the system tray icon
"""

import sys
import os
import time
import threading
import requests

# Make sure imports from desktop/ work
sys.path.insert(0, os.path.dirname(__file__))
# Make sure app/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def start_backend():
    """Run Flask in a background thread."""
    from app.app import app, init_db
    init_db()
    app.run(port=5000, debug=False, use_reloader=False)


def wait_for_backend(retries=20, delay=0.3):
    """Block until the backend is accepting connections."""
    for _ in range(retries):
        try:
            requests.get("http://localhost:5000/health", timeout=1)
            return True
        except Exception:
            time.sleep(delay)
    return False


if __name__ == "__main__":
    #  Start backend
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    #  Wait for it
    if not wait_for_backend():
        print("ERROR: Backend did not start. Check app/app.py for errors.")
        sys.exit(1)

    print("Backend ready.")

    # Import and run the desktop window
    from window import FocusApp
    from tray import run_tray

    app_window = FocusApp()
    run_tray(app_window)

    app_window.protocol("WM_DELETE_WINDOW", app_window.on_close)
    app_window.mainloop()