"""
notifier.py — desktop notifications for Linux
Uses notify-send (built into most distros) with plyer as fallback.
"""

import subprocess


def notify(title: str, message: str):
    """Fire a desktop notification. Silent on failure."""
    try:
        subprocess.Popen(
            ["notify-send", title, message, "--icon=dialog-information"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # notify-send not available — try plyer
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=6)
        except Exception:
            pass