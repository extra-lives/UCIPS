# UCIPS: You See IPs

A small Windows-friendly desktop utility that shows your internal and external IP addresses in a compact window and system tray menu. It updates automatically on a timer and lets you refresh on demand.

## Features

- Shows internal (LAN) and external (public) IPs
- System tray icon with quick actions (Show/Hide, Refresh, Quit)
- Auto-refresh every hour (configurable in `main.py`)
- Lightweight Tkinter UI

## Requirements

- Python 3.9+ (3.8+ should work)
- Packages:
  - `pystray`
  - `Pillow`

## Install

```bash
pip install pystray Pillow
```

## Run

```bash
python main.py
```

## Notes

- External IP lookup uses `https://api.ipify.org?format=json`.
- Close the window to send it to the tray; use the tray menu to quit.

## Customize

- Refresh interval: edit `REFRESH_SECONDS` in `main.py`.
- Tray icon: edit `create_tray_image()` in `main.py`.
