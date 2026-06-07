"""Central settings for the local Jarvis assistant."""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt.txt"
LOG_DIR = BASE_DIR / "logs"

ASSISTANT_NAME = "Jarvis"
HOTWORD = "jarvis"

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma4:e2b-it-qat"
OLLAMA_TIMEOUT_SECONDS = 30

WHISPER_MODEL = "small"
LISTEN_SECONDS = 5
SAMPLE_RATE = 16_000

TTS_RATE = 175
TTS_VOLUME = 1.0

SCREENSHOT_DIR = Path.home() / "Desktop" / "Jarvis Screenshots"

APP_ALIASES = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
}
