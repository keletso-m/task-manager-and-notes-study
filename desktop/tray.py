"""
tray.py — system tray icon
Right-click the tray icon to open or quit Focus.
"""

import threading
import pystray
from PIL import Image, ImageDraw


def _make_icon():
    """Generate a simple coloured circle as the tray icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill="#e94560")
    draw.text((20, 18), "F", fill="white")
    return img


def run_tray(app_window):
    """
    Start the system tray icon in a background thread.
    app_window is the FocusApp (CTk) instance.
    """

    def on_open(icon, item):
        app_window.after(0, app_window.deiconify)

    def on_quit(icon, item):
        icon.stop()
        app_window.after(0, app_window.destroy)

    icon = pystray.Icon(
        "Focus",
        _make_icon(),
        "Focus",
        menu=pystray.Menu(
            pystray.MenuItem("Open Focus", on_open, default=True),
            pystray.MenuItem("Quit",       on_quit),
        ),
    )

    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon