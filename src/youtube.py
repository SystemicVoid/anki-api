"""YouTube transcript extraction utilities."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

__all__ = [
    "is_youtube_url",
    "extract_video_id",
    "export_transcript_to_markdown",
]

# YouTube URL patterns (video ID is always 11 characters)
YOUTUBE_PATTERNS = [
    r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
    r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})",
]


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL. Returns None if not a valid YouTube URL."""
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube video URL."""
    return extract_video_id(url) is not None


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def export_transcript_to_markdown(url: str, output_dir: Path) -> Path:
    """
    Fetch YouTube transcript and save as markdown.

    Args:
        url: YouTube video URL
        output_dir: Directory to save markdown file

    Returns:
        Path to created markdown file

    Raises:
        ValueError: If URL invalid or transcript unavailable
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {url}")

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
    except TranscriptsDisabled:
        raise ValueError(f"Transcripts are disabled for video: {video_id}")
    except NoTranscriptFound:
        raise ValueError(f"No transcript found for video: {video_id}")
    except VideoUnavailable:
        raise ValueError(f"Video unavailable: {video_id}")

    # Build markdown content
    lines = [
        "# YouTube Video Transcript",
        "",
        f"**Video ID:** {video_id}",
        f"**URL:** https://youtube.com/watch?v={video_id}",
        f"**Language:** {transcript.language} ({transcript.language_code})",
        f"**Auto-generated:** {'Yes' if transcript.is_generated else 'No'}",
        "",
        "---",
        "",
        "## Transcript",
        "",
    ]

    for snippet in transcript.snippets:
        timestamp = _format_timestamp(snippet.start)
        lines.append(f"[{timestamp}] {snippet.text}")

    lines.append("")

    # Generate filename and save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"youtube_{video_id}_{timestamp}.md"
    output_path = output_dir / filename

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return output_path
