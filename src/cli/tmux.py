"""Tmux session management for CLI."""

import subprocess
from pathlib import Path

TMUX_SESSION = "anki-flow"
PROJECT_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = PROJECT_DIR / "web" / "frontend"


def tmux_session_exists() -> bool:
    """Check if anki-flow tmux session exists."""
    result = subprocess.run(
        ["tmux", "has-session", "-t", TMUX_SESSION],
        capture_output=True,
    )
    return result.returncode == 0


def tmux_kill_session() -> bool:
    """Kill the anki-flow tmux session."""
    result = subprocess.run(
        ["tmux", "kill-session", "-t", TMUX_SESSION],
        capture_output=True,
    )
    return result.returncode == 0


def tmux_attach_session() -> None:
    """Attach to the anki-flow tmux session."""
    subprocess.run(["tmux", "attach", "-t", TMUX_SESSION])


def tmux_create_session() -> bool:
    """Create tmux session with backend and frontend panes."""
    backend_cmd = f"cd {PROJECT_DIR} && uv run anki-api serve"
    frontend_cmd = f"cd {FRONTEND_DIR} && pnpm dev"

    # Create session with backend in first pane
    result = subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",  # detached
            "-s",
            TMUX_SESSION,
            "-n",
            "servers",
            "-c",
            str(PROJECT_DIR),
            backend_cmd,
        ]
    )
    if result.returncode != 0:
        return False

    # Split horizontally and run frontend in bottom pane
    subprocess.run(
        [
            "tmux",
            "split-window",
            "-t",
            f"{TMUX_SESSION}:servers",
            "-v",  # vertical split (top/bottom)
            "-c",
            str(FRONTEND_DIR),
            frontend_cmd,
        ]
    )

    # Select top pane (backend) as active
    subprocess.run(["tmux", "select-pane", "-t", f"{TMUX_SESSION}:servers.0"])

    return True
