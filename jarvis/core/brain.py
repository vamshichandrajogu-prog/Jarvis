"""Intent parsing and response generation through local Ollama."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

import config


class Brain:
    def __init__(self, prompt_path=config.PROMPT_PATH) -> None:
        self.system_prompt = prompt_path.read_text(encoding="utf-8")
        self.history: list[dict[str, str]] = []

    def understand(self, text: str) -> dict[str, Any]:
        if self._is_clear_memory_command(text):
            self.history = []
            return {
                "action": "chat",
                "value": "",
                "reply": "Memory cleared, starting fresh sir.",
            }

        payload = {
            "model": config.OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                *self.history,
                {"role": "user", "content": text},
            ],
            "format": "json",
        }

        try:
            raw = self._ollama_chat(payload)
            content = raw.get("message", {}).get("content", "")
            intent = self._parse_json(content, text)
            self._remember(text, content, intent)
            return intent
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            return {
                "action": "general_answer",
                "value": text,
                "reply": f"I could not reach Ollama or parse the response: {exc}",
            }

    def _ollama_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{config.OLLAMA_HOST}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.OLLAMA_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))

    def _parse_json(self, content: str, original_text: str) -> dict[str, Any]:
        response = re.sub(r"```json|```", "", content).strip()
        response = response.replace("\\'", "'")

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    parsed = self._parse_reply_fallback(response, original_text)
            else:
                parsed = self._parse_reply_fallback(response, original_text)

        intent = {
            "action": str(parsed.get("action") or "general_answer"),
            "value": parsed.get("value") or original_text,
            "reply": str(parsed.get("reply") or "Done, sir."),
        }
        intent["reply"] = self._sanitize_reply(intent["reply"])
        return intent

    def _sanitize_reply(self, reply: str) -> str:
        # Remove any raw JSON accidentally included in reply.
        reply = re.sub(r"\{.*?\}", "", reply, flags=re.DOTALL).strip()
        # Remove zero-width characters and excessive spaces.
        reply = re.sub(r"[\u200b-\u200f\u202a-\u202e\uFEFF]", "", reply)
        reply = re.sub(r"\s+", " ", reply).strip()
        if not reply or len(reply) < 3:
            return "Done, sir."
        return reply

    def _parse_reply_fallback(self, response: str, original_text: str) -> dict[str, Any]:
        reply_match = re.search(
            r'"reply"\s*:\s*"(.*?)"(?:\s*[,}])',
            response,
            re.DOTALL,
        )
        if reply_match:
            return {
                "action": "chat",
                "value": original_text,
                "reply": reply_match.group(1).strip(),
            }

        return {
            "action": "chat",
            "value": original_text,
            "reply": response.strip() or "I had trouble reading that response, sir.",
        }

    def _remember(self, user_text: str, assistant_content: str, intent: dict[str, Any]) -> None:
        reply_only = intent.get("reply", "").strip()[:100]
        self.history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": reply_only},
            ]
        )
        self.history = self.history[-10:]

    def _is_clear_memory_command(self, text: str) -> bool:
        return text.strip().lower() in {
            "clear memory",
            "forget everything",
            "start over",
        }
