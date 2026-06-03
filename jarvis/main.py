"""Entry point for the Jarvis listen-understand-execute-speak loop."""

from __future__ import annotations

import argparse
import time

import config
from core.brain import Brain
from core.executor import Executor
from core.listener import Listener
from core.speaker import Speaker
from utils.logger import get_logger


def wait_for_spacebar() -> None:
    try:
        import keyboard
    except ImportError as exc:
        raise RuntimeError(
            "Install the keyboard library first: py -3.11 -m pip install keyboard"
        ) from exc

    keyboard.wait("space")
    while keyboard.is_pressed("space"):
        time.sleep(0.05)


def run_once(text: str, brain: Brain, executor: Executor, speaker: Speaker) -> None:
    logger = get_logger()
    logger.info("user: %s", text)

    intent = brain.understand(text)
    logger.info("intent: %s", intent)

    result = executor.execute(intent)
    reply = result.get("reply") or intent.get("reply") or "Done, sir."
    logger.info("reply: %s", reply)
    speaker.speak(reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Jarvis locally.")
    parser.add_argument("--text", help="Run one command without microphone input.")
    parser.add_argument("--typed", action="store_true", help="Use typed commands in a loop.")
    args = parser.parse_args()

    brain = Brain()
    executor = Executor()
    speaker = Speaker()

    if args.text:
        run_once(args.text, brain, executor, speaker)
        return

    if args.typed:
        while True:
            text = input("You: ").strip()
            if text.lower() in {"exit", "quit", "stop"}:
                break
            if text:
                run_once(text, brain, executor, speaker)
        return

    listener = Listener()
    speaker.speak("Jarvis online.")
    print("Press SPACE to speak...")
    while True:
        wait_for_spacebar()
        print(f"Listening for {config.LISTEN_SECONDS} seconds...")
        text = listener.listen_for_command()
        if not text:
            print("Press SPACE to speak...")
            continue
        if text.lower() in {"exit", "quit", "stop jarvis"}:
            speaker.speak("Shutting down, sir.")
            break
        run_once(text, brain, executor, speaker)
        print("Press SPACE to speak...")


if __name__ == "__main__":
    main()
