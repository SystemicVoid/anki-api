"""WebSocket endpoint for real-time card generation with Claude Agent SDK."""

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
)

router = APIRouter()

# Project root and output directories
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CARDS_DIR = PROJECT_ROOT / "cards"
SCRAPED_DIR = PROJECT_ROOT / "scraped"
SCRAPE_SCRIPT = PROJECT_ROOT / "scrape.sh"

# Active generation sessions
active_sessions: Dict[str, "GenerationSession"] = {}


class GenerationSession:
    """Manages a single card generation session."""

    def __init__(self, session_id: str, websocket: WebSocket):
        self.session_id = session_id
        self.websocket = websocket
        self.source: Optional[str] = None
        self.tags: Optional[str] = None
        self.scraped_path: Optional[str] = None
        self.output_file: Optional[str] = None

    async def send_event(self, event_type: str, data: dict):
        """Send JSON event to WebSocket client."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await self.websocket.send_json(message)
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")

    async def scrape_url(self, url: str) -> str:
        """Scrape URL to markdown using scrape.sh script."""
        if not SCRAPE_SCRIPT.exists():
            raise FileNotFoundError(f"Scrape script not found: {SCRAPE_SCRIPT}")

        await self.send_event("status", {
            "message": "Scraping content from URL...",
            "step": "scraping"
        })

        # Run scrape script in background thread to avoid blocking
        def run_scrape():
            import subprocess
            result = subprocess.run(
                [str(SCRAPE_SCRIPT), url],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Scraping failed: {result.stderr}")
            return result.stdout

        try:
            output = await asyncio.to_thread(run_scrape)

            # Extract filename from scrape script output (looks for "scraped/filename.md")
            match = re.search(r"scraped/([^\s]+\.md)", output)
            if match:
                scraped_file = match.group(1)
                scraped_path = SCRAPED_DIR / scraped_file
                if scraped_path.exists():
                    self.scraped_path = str(scraped_path)
                    await self.send_event("status", {
                        "message": f"Content scraped successfully: {scraped_file}",
                        "step": "scraping_complete"
                    })
                    return self.scraped_path

            # Fallback: find most recent .md file in scraped/
            scraped_files = list(SCRAPED_DIR.glob("*.md"))
            if scraped_files:
                most_recent = max(scraped_files, key=lambda p: p.stat().st_mtime)
                self.scraped_path = str(most_recent)
                await self.send_event("status", {
                    "message": f"Content scraped: {most_recent.name}",
                    "step": "scraping_complete"
                })
                return self.scraped_path

            raise RuntimeError("Scraping completed but no output file found")

        except Exception as e:
            await self.send_event("error", {
                "message": f"Scraping failed: {str(e)}",
                "step": "scraping"
            })
            raise

    async def validate_source(self, source: str) -> str:
        """Validate and prepare source (URL or file path)."""
        print(f"[DEBUG] Validating source: {source}")

        # Determine if source is URL or file path
        if source.startswith(("http://", "https://")):
            # URL - scrape it
            print(f"[DEBUG] Source is URL, will scrape")
            return await self.scrape_url(source)
        else:
            # File path - validate it exists
            file_path = Path(source)

            # Handle relative paths by resolving against project root
            if not file_path.is_absolute():
                file_path = PROJECT_ROOT / source
                print(f"[DEBUG] Relative path converted to: {file_path}")
            else:
                print(f"[DEBUG] Absolute path provided: {file_path}")

            # Check if file exists
            if not file_path.exists():
                # Provide helpful error with suggestions
                parent_dir = file_path.parent
                if parent_dir.exists():
                    similar_files = list(parent_dir.glob("*" + file_path.stem[:20] + "*"))
                    error_msg = f"Source file not found: {file_path}\n"
                    if similar_files:
                        error_msg += f"Similar files in {parent_dir.name}/:\n"
                        for f in similar_files[:5]:
                            error_msg += f"  - {f.name}\n"
                    await self.send_event("error", {
                        "message": error_msg,
                        "step": "validation"
                    })
                    raise FileNotFoundError(error_msg)
                else:
                    error_msg = f"Source file not found and parent directory doesn't exist: {file_path}"
                    await self.send_event("error", {
                        "message": error_msg,
                        "step": "validation"
                    })
                    raise FileNotFoundError(error_msg)

            if not file_path.is_file():
                error_msg = f"Source is not a file: {file_path}"
                await self.send_event("error", {
                    "message": error_msg,
                    "step": "validation"
                })
                raise ValueError(error_msg)

            print(f"[DEBUG] File validated successfully: {file_path}")
            await self.send_event("status", {
                "message": f"Using existing file: {file_path.name}",
                "step": "source_ready"
            })
            return str(file_path)

    async def generate_cards(self, source_path: str):
        """Generate cards using Claude Agent SDK."""
        await self.send_event("status", {
            "message": "Starting card generation with Claude Agent...",
            "step": "generating"
        })

        # Build prompt for agent
        prompt_parts = ["/create-anki-cards", source_path]
        if self.tags:
            prompt_parts.extend(["--tags", self.tags])
        prompt = " ".join(prompt_parts)

        print(f"[DEBUG] Prompt: {prompt}")
        print(f"[DEBUG] CWD: {PROJECT_ROOT}")

        # Configure Claude Agent SDK
        options = ClaudeAgentOptions(
            cwd=str(PROJECT_ROOT),
            allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"],
            permission_mode="acceptEdits",  # Auto-approve file writes to cards/
            max_turns=20,  # Increase turns for complex generation
            setting_sources=["project", "user"],  # Load project settings (skills)
        )

        try:
            # Stream messages from agent
            message_count = 0
            async for message in query(prompt=prompt, options=options):
                message_count += 1
                print(f"[DEBUG] Message {message_count}: {type(message).__name__}")
                await self.process_sdk_message(message)

            print(f"[DEBUG] Total messages received: {message_count}")

            # Find generated output file
            self.output_file = await self.find_output_file()
            print(f"[DEBUG] Output file: {self.output_file}")

            if self.output_file:
                await self.send_event("complete", {
                    "filename": Path(self.output_file).name,
                    "message": f"Generated flashcards successfully",
                })
            else:
                await self.send_event("error", {
                    "message": "Card generation completed but no output file found",
                    "step": "generating"
                })

        except Exception as e:
            print(f"[DEBUG] Exception in generate_cards: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await self.send_event("error", {
                "message": f"Generation failed: {str(e)}",
                "step": "generating"
            })
            raise

    async def process_sdk_message(self, message):
        """Process and forward SDK messages to WebSocket client."""
        print(f"[DEBUG] Processing message type: {type(message).__name__}")
        print(f"[DEBUG] Message dir: {[attr for attr in dir(message) if not attr.startswith('_')]}")

        if isinstance(message, AssistantMessage):
            print(f"[DEBUG] AssistantMessage content blocks: {len(message.content)}")
            for block in message.content:
                print(f"[DEBUG]   Block type: {type(block).__name__}")
                if isinstance(block, TextBlock):
                    # Agent thinking/explanation
                    await self.send_event("text", {
                        "content": block.text
                    })
                elif isinstance(block, ToolUseBlock):
                    # Tool call (Read, Write, etc.)
                    await self.send_event("tool", {
                        "name": block.name,
                        "input": block.input,
                    })
        else:
            # Log other message types for debugging
            print(f"[DEBUG] Unhandled message type: {type(message).__name__}")
            if hasattr(message, 'type'):
                print(f"[DEBUG]   message.type: {message.type}")
            if hasattr(message, 'subtype'):
                print(f"[DEBUG]   message.subtype: {getattr(message, 'subtype', 'N/A')}")

    async def find_output_file(self) -> Optional[str]:
        """Find the most recently created file in cards/ directory."""
        if not CARDS_DIR.exists():
            return None

        json_files = list(CARDS_DIR.glob("*.json"))
        if not json_files:
            return None

        # Return most recent file
        most_recent = max(json_files, key=lambda p: p.stat().st_mtime)
        return str(most_recent)


@router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for real-time card generation."""
    await websocket.accept()

    session_id = str(uuid4())
    session = GenerationSession(session_id, websocket)
    active_sessions[session_id] = session

    try:
        # Receive initial request with source and optional tags
        request_data = await websocket.receive_json()
        source = request_data.get("source")
        tags = request_data.get("tags", "")

        print(f"[DEBUG] WebSocket received request_data: {request_data}")
        print(f"[DEBUG] Source: {repr(source)}")
        print(f"[DEBUG] Source bytes: {source.encode('utf-8') if source else None}")
        print(f"[DEBUG] Tags: {repr(tags)}")

        if not source:
            await session.send_event("error", {
                "message": "Missing 'source' parameter",
                "step": "validation"
            })
            return

        session.source = source
        session.tags = tags

        # Validate and prepare source (scrape URL or validate file)
        source_path = await session.validate_source(source)

        # Generate cards with Claude Agent SDK
        await session.generate_cards(source_path)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"Error in generation session {session_id}: {e}")
        try:
            await session.send_event("error", {
                "message": str(e),
                "step": "unknown"
            })
        except:
            pass
    finally:
        # Cleanup
        active_sessions.pop(session_id, None)
        try:
            await websocket.close()
        except:
            pass
