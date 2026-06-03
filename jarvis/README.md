# Jarvis

Local, offline-first personal voice assistant based on the PRD in `Jarvis_PRD.docx`.

## Setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Install and start Ollama, then pull a local model:

```powershell
ollama pull llama3
ollama serve
```

## Run

Typed command mode is the easiest first test:

```powershell
python main.py --typed
```

Run one command:

```powershell
python main.py --text "open YouTube"
```

Run voice mode:

```powershell
python main.py
```

## Flow

1. `core/listener.py` records microphone audio and transcribes with Whisper.
2. `core/brain.py` sends text to Ollama and expects a JSON intent.
3. `core/executor.py` routes the intent to `skills/`.
4. `core/speaker.py` speaks the response with `pyttsx3`.
5. `utils/logger.py` logs commands, intents, and replies.

