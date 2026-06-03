"""Text-to-speech output."""

from __future__ import annotations

import config


class Speaker:
    def __init__(self) -> None:
        pass

    def speak(self, text: str) -> None:
        print(f"Jarvis: {text}")
        engine = None
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", config.TTS_RATE)
            engine.setProperty("volume", config.TTS_VOLUME)
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            print(f"TTS failed: {exc}")
        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass
