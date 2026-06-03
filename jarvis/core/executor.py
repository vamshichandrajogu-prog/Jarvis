"""Route parsed intents to concrete skills."""

from __future__ import annotations

from typing import Any, Callable

from skills import apps, browser, files, system


class Executor:
    def __init__(self) -> None:
        self.routes: dict[str, Callable[[Any], str]] = {
            "open_url": browser.open_url,
            "search_google": browser.search_google,
            "search_youtube": browser.search_youtube,
            "open_in_chrome": browser.open_in_chrome,
            "open_app": apps.open_app,
            "close_app": apps.close_app,
            "open_folder": apps.open_folder,
            "open_settings": apps.open_settings_page,
            "settings": apps.open_settings_page,
            "open_settings_page": apps.open_settings_page,
            "open_spotify": apps.open_spotify,
            "read_file": files.read_file,
            "take_screenshot": system.take_screenshot,
            "set_volume": system.set_volume,
            "system_cmd": system.system_command,
        }

    def execute(self, intent: dict[str, Any]) -> dict[str, str]:
        action = str(intent.get("action") or "general_answer")
        value = intent.get("value")
        reply = str(intent.get("reply") or "Done, sir.")

        if action == "tell_joke":
            # Model sometimes puts joke in value instead of reply.
            joke = intent.get("reply", "")
            if joke.lower().strip() in {"done, sir.", "done.", ""}:
                joke = intent.get(
                    "value",
                    "Here is a joke: Why did the programmer quit? Because he did not get arrays!",
                )
            return {"reply": joke}

        if action in {"general_answer", "chat"}:
            return {"reply": reply}

        handler = self.routes.get(action)
        if not handler:
            return {"reply": f"I do not know how to run action '{action}' yet."}

        try:
            outcome = handler(value)
            return {"reply": outcome if outcome else reply}
        except Exception as exc:
            return {"reply": f"I could not complete that action: {exc}"}
