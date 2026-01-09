import json
import socket
import threading
import time
import tkinter as tk
import urllib.error
import urllib.request

import pystray
from PIL import Image, ImageDraw

APP_TITLE = "UCIPS: You See IPs"
REFRESH_SECONDS = 60 * 60  # 1 hour
EXTERNAL_IP_URL = "https://api.ipify.org?format=json"


def get_internal_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except OSError:
        return "Unavailable"


def get_external_ip():
    try:
        with urllib.request.urlopen(EXTERNAL_IP_URL, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("ip", "Unavailable")
    except (urllib.error.URLError, ValueError, TimeoutError):
        return "Unavailable"


class IPApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.status_var = tk.StringVar(value="Checking...")
        self.internal_ip_var = tk.StringVar(value="--")
        self.external_ip_var = tk.StringVar(value="--")
        self.tray_icon = None
        self.window_visible = True

        frame = tk.Frame(root, padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        internal_block = tk.Frame(frame)
        internal_block.pack(anchor="w")
        tk.Label(internal_block, textvariable=self.internal_ip_var, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(internal_block, text="Internal", font=("Segoe UI", 8)).pack(anchor="w")

        external_block = tk.Frame(frame)
        external_block.pack(anchor="w", pady=(6, 0))
        tk.Label(external_block, textvariable=self.external_ip_var, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(external_block, text="External", font=("Segoe UI", 8)).pack(anchor="w")

        tk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 9), fg="#666666").pack(anchor="w", pady=(6, 0))

        btn_row = tk.Frame(frame)
        btn_row.pack(anchor="w", pady=(8, 0))

        tk.Button(btn_row, text="Refresh", command=self.refresh).pack(side="left")
        tk.Button(btn_row, text="Quit", command=self.root.destroy).pack(side="left", padx=(6, 0))

        self.refresh()
        self.schedule_refresh()
        self.setup_tray()
        self.hide_window()

    def setup_tray(self):
        image = self.create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Show/Hide", self.toggle_window),
            pystray.MenuItem("Refresh", self.refresh_from_tray),
            pystray.MenuItem("Quit", self.quit_from_tray),
        )
        self.tray_icon = pystray.Icon("ucips", image, "UCIPS", menu)
        self.update_tray_title()
        self.tray_icon.run_detached()

    def create_tray_image(self):
        size = 64
        image = Image.new("RGB", (size, size), "#1b1f23")
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, size - 8, size - 8), outline="#4fa3ff", width=3)
        draw.text((18, 20), "IP", fill="#4fa3ff")
        return image

    def update_tray_title(self):
        if not self.tray_icon:
            return
        internal = self.internal_ip_var.get()
        external = self.external_ip_var.get()
        self.tray_icon.title = f"Internal IP: {internal} / External IP: {external}"

    def refresh_from_tray(self, _icon=None, _item=None):
        self.root.after(0, self.refresh)

    def quit_from_tray(self, _icon=None, _item=None):
        self.root.after(0, self.quit_app)

    def toggle_window(self, _icon=None, _item=None):
        if self.window_visible:
            self.hide_window()
        else:
            self.show_window()

    def hide_window(self):
        self.root.withdraw()
        self.window_visible = False

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.window_visible = True

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()

    def refresh(self):
        self.status_var.set("Refreshing...")
        self.internal_ip_var.set(get_internal_ip())
        self.update_tray_title()

        def worker():
            external = get_external_ip()
            self.root.after(0, self.update_external, external)

        threading.Thread(target=worker, daemon=True).start()

    def update_external(self, external_ip):
        self.external_ip_var.set(external_ip)
        self.update_tray_title()
        timestamp = time.strftime("%H:%M:%S")
        self.status_var.set(f"Last update: {timestamp}")

    def schedule_refresh(self):
        self.root.after(REFRESH_SECONDS * 1000, self.on_timer)

    def on_timer(self):
        self.refresh()
        self.schedule_refresh()


if __name__ == "__main__":
    root = tk.Tk()
    app = IPApp(root)
    root.mainloop()
