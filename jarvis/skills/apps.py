"""Application launch and close skills for Windows."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import config


def open_app(value) -> str:
    app_name = str(value or "").strip().lower()
    if not app_name:
        return "No application name was provided."

    uri_map = {
        "whatsapp": "start whatsapp:",
        "settings": "start ms-settings:",
        "microsoft store": "start ms-windows-store:",
        "xbox": "start xbox:",
        "mail": "start outlookmail:",
        "calendar": "start outlookcal:",
        "photos": "start ms-photos:",
    }
    if app_name in uri_map:
        os.system(uri_map[app_name])
        return f"Opening {app_name}, sir."

    alias = config.APP_ALIASES.get(app_name)
    if alias:
        subprocess.Popen(alias, shell=True)
        return f"Opening {app_name}, sir."

    lnk_path = _find_start_menu_shortcut(app_name)
    if lnk_path:
        os.startfile(str(lnk_path))
        return f"Opening {app_name}, sir."

    app_id = _find_start_app_id(app_name)
    if app_id:
        subprocess.Popen(f"explorer.exe shell:AppsFolder\\{app_id}", shell=True)
        return f"Opening {app_name}, sir."

    os.system(f'start "" "{app_name}"')
    return f"Trying to open {app_name}, sir."


def close_app(value) -> str:
    app_name = str(value or "").strip().lower()
    if app_name == "whatsapp":
        subprocess.run("taskkill /IM WhatsApp.exe /F", shell=True, capture_output=True)
        subprocess.run("taskkill /IM WinStore.App.exe /F", shell=True, capture_output=True)
        return "Closing WhatsApp, sir."

    if not app_name:
        return "No application name was provided."

    tasklist_output = _get_verbose_tasklist()
    tasklist_lines = tasklist_output.splitlines()

    process_map = {
        "whatsapp": "WhatsApp.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
        "spotify": "Spotify.exe",
        "vscode": "Code.exe",
        "vs code": "Code.exe",
        "visual studio code": "Code.exe",
        "firefox": "firefox.exe",
        "telegram": "Telegram.exe",
        "discord": "Discord.exe",
        "zoom": "Zoom.exe",
        "vlc": "vlc.exe",
        "file explorer": "explorer.exe",
    }

    tasklist_output_lower = tasklist_output.lower()
    process_name = process_map.get(app_name)
    if process_name:
        if process_name.lower() not in tasklist_output_lower:
            return f"{app_name} does not appear to be running, sir."
        subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            check=False,
            capture_output=True,
        )
        return f"Closing {app_name}, sir."

    for line in tasklist_lines:
        if app_name in line.lower():
            process_name = line.split()[0]
            subprocess.run(
                ["taskkill", "/IM", process_name, "/F"],
                check=False,
                capture_output=True,
            )
            return f"Closing {app_name}, sir."

    return f"{app_name} does not appear to be running, sir."


def open_folder(value) -> str:
    folder_name = str(value or "").strip().lower()
    if not folder_name:
        return "No folder was provided."

    folder_map = {
        "downloads": str(Path.home() / "Downloads"),
        "desktop": str(Path.home() / "Desktop"),
        "documents": str(Path.home() / "Documents"),
        "pictures": str(Path.home() / "Pictures"),
        "music": str(Path.home() / "Music"),
        "videos": str(Path.home() / "Videos"),
        "appdata": str(Path(os.environ.get("APPDATA", ""))),
        "thispc": "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
        "this pc": "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
        "my computer": "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
    }
    folder_path = folder_map.get(folder_name, str(value or "").strip())
    if folder_path.startswith("::"):
        subprocess.Popen(["explorer.exe", folder_path])
        return "Opening This PC, sir."

    folder_path = Path(folder_path).expanduser()
    if not folder_path.exists() or not folder_path.is_dir():
        return f"I could not find the folder: {folder_path}"

    subprocess.Popen(["explorer.exe", str(folder_path)])
    return f"Opening {folder_name} folder, sir."


def open_settings_page(value) -> str:
    page_name = str(value or "").strip().lower()
    settings_map = {
        "wifi": "ms-settings:network-wifi",
        "bluetooth": "ms-settings:bluetooth",
        "display": "ms-settings:display",
        "sound": "ms-settings:sound",
        "battery": "ms-settings:batterysaver",
        "storage": "ms-settings:storagesense",
        "apps": "ms-settings:appsfeatures",
        "startup": "ms-settings:startupapps",
        "update": "ms-settings:windowsupdate",
        "privacy": "ms-settings:privacy",
        "accounts": "ms-settings:accounts",
        "notifications": "ms-settings:notifications",
        "default": "ms-settings:",
    }
    uri = settings_map.get(page_name, settings_map["default"])
    os.system(f"start {uri}")
    label = page_name or "default"
    return f"Opening {label} settings, sir."


def open_spotify(value) -> str:
    query = str(value or "").strip()
    if query:
        os.system(f"start spotify:search:{query.replace(' ', '%20')}")
        return f"Searching Spotify for {query}, sir."

    os.system("start spotify:")
    return "Opening Spotify, sir."


def _find_start_menu_shortcut(app_name: str) -> Path | None:
    start_menu_paths = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
        Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs"),
    ]

    for start_path in start_menu_paths:
        if not start_path.exists():
            continue
        try:
            for lnk_path in start_path.rglob("*.lnk"):
                if app_name in lnk_path.stem.lower():
                    return lnk_path
        except (OSError, PermissionError):
            continue

    return None


def _find_start_app_id(app_name: str) -> str:
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            f"Get-StartApps | Where-Object {{$_.Name -like '*{app_name}*'}} | "
            "Select-Object -First 1 -ExpandProperty AppID",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return result.stdout.strip()


def _get_verbose_tasklist() -> str:
    result = subprocess.run(
        ["tasklist", "/V"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout or ""
