"""Microphone input and local Whisper transcription."""

from __future__ import annotations
import os
os.environ["PATH"] += r";C:\Users\vamsh\Downloads\ffmpeg-master-latest-win64-gpl-shared\bin"

import tempfile
import wave
from pathlib import Path

import config


class Listener:
    def __init__(self) -> None:
        self._whisper_model = None

    def listen_for_command(self) -> str:
        try:
            text = self.transcribe_microphone()
        except Exception as exc:
            print(f"Microphone transcription failed: {exc}")
            text = input("Type command instead: ")

        cleaned = text.strip()
        # Ignore if too short -- likely silence or noise.
        if len(cleaned.split()) < 2:
            return ""

        # Ignore common Whisper hallucinations from silence.
        HALLUCINATIONS = {
            "thank you",
            "thanks",
            "thank you very much",
            "thanks for watching",
            "you",
            "the",
            "bye",
            "goodbye",
            "please",
            "okay",
            "ok",
            "um",
            "uh",
            "hmm",
            "ah",
            "oh",
            "hey",
            "hi",
            "hello",
        }
        if cleaned.lower().strip(".!?,") in HALLUCINATIONS:
            return ""

        lowered = cleaned.lower()
        if lowered.startswith(f"hey {config.HOTWORD}"):
            return cleaned[len(f"hey {config.HOTWORD}") :].strip()
        if lowered.startswith(config.HOTWORD):
            return cleaned[len(config.HOTWORD) :].strip()
        return cleaned

    def transcribe_microphone(self) -> str:
        try:
            import sounddevice as sd
            import whisper
        except ImportError as exc:
            raise RuntimeError("Install audio dependencies from requirements.txt first.") from exc

        recording = sd.rec(
            int(config.LISTEN_SECONDS * config.SAMPLE_RATE),
            samplerate=config.SAMPLE_RATE,
            channels=1,
            dtype="int16",
        )
        sd.wait()

        wav_path = self._write_wav(recording)
        try:
            if self._whisper_model is None:
                self._whisper_model = whisper.load_model(config.WHISPER_MODEL)
            result = self._whisper_model.transcribe(str(wav_path), fp16=False)
            return str(result.get("text", "")).strip()
        finally:
            wav_path.unlink(missing_ok=True)

    def _write_wav(self, recording) -> Path:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wav_path = Path(temp_file.name)
        with wave.open(str(wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(config.SAMPLE_RATE)
            wav_file.writeframes(recording.tobytes())
        return wav_path
