"""Browser and web search skills."""

from __future__ import annotations

import subprocess
import urllib.parse
import webbrowser


def open_url(value) -> str:
    url = str(value or "").strip()
    if not url:
        return "No URL was provided."

    parsed_url = _parse_url(url)
    has_query_path = bool(parsed_url.path.strip("/") or parsed_url.query)
    normalized = (parsed_url.netloc or parsed_url.path).lower()
    if "youtube" in normalized and not has_query_path:
        webbrowser.open_new_tab("https://www.youtube.com")
        return "Opening YouTube, sir."
    if "google" in normalized and not has_query_path:
        webbrowser.open_new_tab("https://www.google.com")
        return "Opening Google, sir."

    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open_new_tab(url)
    return "Opening that page, sir."


def _parse_url(url: str) -> urllib.parse.ParseResult:
    if url.startswith(("http://", "https://")):
        return urllib.parse.urlparse(url)
    return urllib.parse.urlparse("https://" + url)


def search_google(value) -> str:
    query = urllib.parse.quote_plus(str(value or "").strip())
    if not query:
        return "No search query was provided."
    webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")
    return "Searching Google, sir."


def search_youtube(value) -> str:
    query = urllib.parse.quote_plus(str(value or "").strip())
    if not query:
        webbrowser.open_new_tab("https://www.youtube.com")
        return "Opening YouTube, sir."
    webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={query}")
    return "Searching YouTube, sir."


def open_in_chrome(value) -> str:
    url = str(value or "").strip()
    if not url:
        return "No URL was provided."
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    subprocess.Popen(["chrome.exe", url], shell=True)
    return f"Opening {url} in Chrome, sir."
