"""File browser routes for selecting content files."""

import os
from pathlib import Path
from typing import List, Literal
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..models import FileNode, FileBrowserResponse

router = APIRouter()

# Project root and allowed directories
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCRAPED_DIR = PROJECT_ROOT / "scraped"
CARDS_DIR = PROJECT_ROOT / "cards"

# Blacklist sensitive directories for system mode
BLOCKED_PATHS = [
    Path("/etc"),
    Path("/root"),
    Path("/sys"),
    Path("/proc"),
    Path("/dev"),
    Path("/boot"),
    Path("/var/lib"),
    Path("/usr/lib"),
]


def is_path_blocked(path: Path) -> bool:
    """Check if path is within blocked directories."""
    try:
        resolved = path.resolve()
        for blocked in BLOCKED_PATHS:
            try:
                resolved.relative_to(blocked)
                return True  # Path is inside blocked directory
            except ValueError:
                continue
        return False
    except (OSError, RuntimeError):
        # Handle resolution errors (e.g., circular symlinks)
        return True


def validate_project_path(path: str, dir_type: Literal["scraped", "cards"]) -> Path:
    """Validate and resolve path for project mode browsing.

    Args:
        path: Relative path within project directory (empty string for root)
        dir_type: Which project directory to browse

    Returns:
        Resolved absolute path

    Raises:
        HTTPException: If path is invalid or outside allowed directory
    """
    base_dir = SCRAPED_DIR if dir_type == "scraped" else CARDS_DIR

    # Create directory if it doesn't exist
    if not base_dir.exists():
        base_dir.mkdir(parents=True, exist_ok=True)

    # Empty path means base directory
    if not path or path == ".":
        return base_dir

    # Construct and resolve full path
    try:
        full_path = (base_dir / path).resolve()
    except (OSError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}")

    # Ensure path is within allowed directory (prevent traversal)
    try:
        full_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access denied: path outside allowed directory"
        )

    return full_path


def validate_system_path(path: str) -> Path:
    """Validate path for system mode browsing.

    Args:
        path: Absolute path or empty for home directory

    Returns:
        Resolved absolute path

    Raises:
        HTTPException: If path is blocked, doesn't exist, or not readable
    """
    # Default to user home directory
    if not path:
        return Path.home()

    try:
        path_obj = Path(path).expanduser().resolve()
    except (OSError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}")

    # Block sensitive directories
    if is_path_blocked(path_obj):
        raise HTTPException(
            status_code=403,
            detail="Access to this directory is not allowed"
        )

    # Check exists
    if not path_obj.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    # Check readable
    if not os.access(path_obj, os.R_OK):
        raise HTTPException(status_code=403, detail="Permission denied")

    return path_obj


def should_include_file(file_path: Path, mode: str, dir_type: str) -> bool:
    """Determine if file should be included in listing.

    Args:
        file_path: Path to file
        mode: "project" or "system"
        dir_type: "scraped" or "cards" (only relevant for project mode)

    Returns:
        True if file should be included
    """
    # Skip hidden files
    if file_path.name.startswith('.'):
        return False

    # In project mode, filter by extension
    if mode == "project" and file_path.is_file():
        if dir_type == "scraped" and file_path.suffix != ".md":
            return False
        if dir_type == "cards" and file_path.suffix != ".json":
            return False

    return True


@router.get("/browse", response_model=FileBrowserResponse)
async def browse_files(
    path: str = "",
    mode: Literal["project", "system"] = "project",
    dir_type: Literal["scraped", "cards"] = "scraped"
):
    """Browse files in project directories or filesystem.

    Args:
        path: Path to browse (relative for project, absolute for system)
        mode: "project" for scraped/cards dirs, "system" for filesystem
        dir_type: Which project directory ("scraped" or "cards")

    Returns:
        FileBrowserResponse with directory contents
    """
    # Validate and resolve path based on mode
    if mode == "project":
        resolved_path = validate_project_path(path, dir_type)
        base_dir = SCRAPED_DIR if dir_type == "scraped" else CARDS_DIR
    else:  # system mode
        resolved_path = validate_system_path(path)
        base_dir = None

    # Must be a directory
    if not resolved_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    # List directory contents
    nodes = []
    try:
        items = list(resolved_path.iterdir())
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Process each item
    for item in items:
        try:
            # Check if we should include this file/directory
            if not should_include_file(item, mode, dir_type):
                continue

            stat = item.stat()

            nodes.append(FileNode(
                name=item.name,
                path=str(item) if mode == "system" else str(item.relative_to(PROJECT_ROOT)),
                type="directory" if item.is_dir() else "file",
                extension=item.suffix if item.is_file() else None,
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                readable=True
            ))
        except (PermissionError, OSError):
            # Mark as unreadable but include in list
            nodes.append(FileNode(
                name=item.name,
                path=str(item) if mode == "system" else str(item.relative_to(PROJECT_ROOT)),
                type="directory" if item.is_dir() else "file",
                extension=None,
                size=0,
                modified=datetime.now(tz=timezone.utc),
                readable=False
            ))

    # Sort: directories first, then by name (case-insensitive)
    nodes.sort(key=lambda x: (x.type != "directory", x.name.lower()))

    # Calculate parent path
    parent_path = None
    if mode == "project":
        if resolved_path != base_dir:
            parent_path = str(resolved_path.parent.relative_to(PROJECT_ROOT))
    else:  # system mode
        if resolved_path.parent != resolved_path:  # Not at root
            parent_path = str(resolved_path.parent)

    return FileBrowserResponse(
        current_path=str(resolved_path) if mode == "system" else str(resolved_path.relative_to(PROJECT_ROOT)),
        parent_path=parent_path,
        nodes=nodes,
        mode=mode
    )


@router.get("/recent", response_model=List[FileNode])
async def get_recent_files(limit: int = 10):
    """Get recently modified files from project directories.

    Args:
        limit: Maximum number of files to return

    Returns:
        List of FileNode objects sorted by modification time (most recent first)
    """
    all_files = []

    # Collect from scraped/ (*.md files)
    if SCRAPED_DIR.exists():
        for f in SCRAPED_DIR.rglob("*.md"):
            if f.is_file() and not f.name.startswith('.'):
                try:
                    stat = f.stat()
                    all_files.append((f, stat.st_mtime))
                except OSError:
                    continue

    # Collect from cards/ (*.json files)
    if CARDS_DIR.exists():
        for f in CARDS_DIR.rglob("*.json"):
            if f.is_file() and not f.name.startswith('.'):
                try:
                    stat = f.stat()
                    all_files.append((f, stat.st_mtime))
                except OSError:
                    continue

    # Sort by modification time (most recent first)
    all_files.sort(key=lambda x: x[1], reverse=True)

    # Convert to FileNode objects
    nodes = []
    for file_path, mtime in all_files[:limit]:
        try:
            stat = file_path.stat()
            nodes.append(FileNode(
                name=file_path.name,
                path=str(file_path.relative_to(PROJECT_ROOT)),
                type="file",
                extension=file_path.suffix,
                size=stat.st_size,
                modified=datetime.fromtimestamp(mtime, tz=timezone.utc),
                readable=True
            ))
        except OSError:
            # Skip if file no longer accessible
            continue

    return nodes
