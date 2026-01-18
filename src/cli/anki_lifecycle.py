"""Anki process management utilities."""

import subprocess
import sys
import time

from src.anki_client import AnkiClient, AnkiConnectError
from src.cli.output import print_error, print_info, print_success


def get_client() -> AnkiClient:
    """Create and return an AnkiClient instance."""
    return AnkiClient()


def is_anki_running() -> bool:
    """Check if Anki Desktop is running via pgrep."""
    result = subprocess.run(["pgrep", "-x", "anki"], capture_output=True)
    return result.returncode == 0


def start_anki_desktop() -> None:
    """Launch Anki Desktop in background."""
    subprocess.Popen(
        ["anki"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_anki_connect(client: AnkiClient, timeout: int = 30) -> bool:
    """Poll AnkiConnect until ready or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            if client.ping():
                return True
        except AnkiConnectError:
            pass
        time.sleep(1)
    return False


def ensure_anki_running(
    client: AnkiClient | None = None, timeout: int = 30
) -> AnkiClient:
    """Ensure Anki Desktop is running and AnkiConnect is responsive.

    Starts Anki Desktop if not already running and waits for AnkiConnect.
    Returns an AnkiClient instance on success, exits on failure.
    """
    if client is None:
        client = get_client()

    # Check if already connected
    try:
        if client.ping():
            return client
    except AnkiConnectError:
        pass

    # Check if Anki process is running
    if not is_anki_running():
        print_info("Anki not running. Starting Anki Desktop...")
        start_anki_desktop()
        time.sleep(2)  # Give Anki time to initialize

    # Wait for AnkiConnect to respond
    print_info("Waiting for AnkiConnect...")
    if not wait_for_anki_connect(client, timeout=timeout):
        print_error(
            "AnkiConnect not responding. Is Anki running with AnkiConnect installed?"
        )
        sys.exit(1)

    print_success("Connected to AnkiConnect")
    return client
