"""System control skills."""

from __future__ import annotations

import subprocess
from datetime import datetime

import config


def take_screenshot(value=None) -> str:
    try:
        import pyautogui
    except ImportError as exc:
        raise RuntimeError("Install pyautogui to take screenshots.") from exc

    config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = config.SCREENSHOT_DIR / filename
    pyautogui.screenshot(str(path))
    return f"Screenshot saved to {path}"


def set_volume(value) -> str:
    direction = str(value or "").lower()
    if "up" in direction or "+" in direction:
        key = "volumeup"
        message = "Volume up, sir."
    elif "down" in direction or "-" in direction:
        key = "volumedown"
        message = "Volume down, sir."
    elif "mute" in direction:
        key = "volumemute"
        message = "Toggling mute, sir."
    else:
        return "Tell me volume up, volume down, or mute."

    try:
        import pyautogui
    except ImportError as exc:
        raise RuntimeError("Install pyautogui to control volume.") from exc

    pyautogui.press(key)
    return message


def system_command(value) -> str:
    command = str(value or "").lower()
    if command in {"shutdown", "shut down"}:
        subprocess.run(["shutdown", "/s", "/t", "30"], check=False)
        return "Shutdown scheduled in 30 seconds, sir."
    if command in {"restart", "reboot"}:
        subprocess.run(["shutdown", "/r", "/t", "30"], check=False)
        return "Restart scheduled in 30 seconds, sir."
    if command in {"cancel shutdown", "abort shutdown"}:
        subprocess.run(["shutdown", "/a"], check=False)
        return "Shutdown cancelled, sir."
    return "That system command is not allowed yet."

