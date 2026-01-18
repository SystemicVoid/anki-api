"""Server and browser utilities for CLI."""

import shutil
import subprocess
import time
from pathlib import Path

import requests

PROJECT_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = PROJECT_DIR / "web" / "frontend"
BACKEND_URL = "http://127.0.0.1:8080"
FRONTEND_URL = "http://localhost:5173"


def run_claude_generation(source: str, tags: str | None) -> bool:
    """Run Claude Code to generate cards. Returns True on success."""
    cmd = ["claude", "-p", "--dangerously-skip-permissions"]
    prompt = f"/create-anki-cards {source}"
    if tags:
        prompt += f" --tags {tags}"
    # Run from PROJECT_DIR so Claude Code finds the skill in .claude/commands/
    result = subprocess.run(cmd + [prompt], cwd=PROJECT_DIR)
    return result.returncode == 0


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Poll URL until it responds or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def open_browser(url: str) -> None:
    """Open URL in default browser."""
    subprocess.Popen(
        ["xdg-open", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def open_browser_chrome(url: str) -> None:
    """Open URL in Chrome if available, otherwise default browser."""
    chrome_commands = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ]

    for cmd in chrome_commands:
        if shutil.which(cmd):
            subprocess.Popen(
                [cmd, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

    # Fallback to xdg-open (default browser)
    open_browser(url)
