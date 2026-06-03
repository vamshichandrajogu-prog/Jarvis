"""File and folder skills."""

from __future__ import annotations

import os
from pathlib import Path


def open_folder(value) -> str:
    folder = Path(str(value or "")).expanduser()
    if not folder.exists() or not folder.is_dir():
        return f"I could not find the folder: {folder}"
    os.startfile(folder)
    return "Opening the folder, sir."


def read_file(value) -> str:
    file_path = Path(str(value or "")).expanduser()
    if not file_path.exists() or not file_path.is_file():
        return f"I could not find the file: {file_path}"
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return text[:1000] if text else "The file is empty."

