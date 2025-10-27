"""
Factory Operations Chatbot - CLI Interface

This module provides the main CLI interface for the factory operations chatbot.
It handles user interaction, Claude API integration, and tool execution.
"""

from datetime import datetime
from typing import Any, Dict, List
import json
import tempfile
import wave
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openai import OpenAI

from .config import API_KEY, MODEL, FACTORY_NAME, RECORDING_DURATION
from .data import initialize_data, data_exists, load_data, MACHINES
from .metrics import (
    calculate_oee,
    get_scrap_metrics,
    get_quality_issues,
    get_downtime_analysis,
)

# Initialize CLI app and console
app = typer.Typer(help="Factory Operations Chatbot - Demo Application")
console = Console()


# Audio utility functions for voice interface
def _record_audio(duration: int = 5) -> Path:
    """Record audio from microphone and save to temporary WAV file.

    Captures audio in 16kHz mono format optimized for OpenAI Whisper API.
    Uses PyAudio for cross-platform recording. Caller must delete returned file.

    Code Flow:
    1. Initialize PyAudio and configure recording parameters (16kHz, mono, 16-bit)
    2. Open audio input stream and record in 1024-frame chunks
    3. Clean up PyAudio resources (guaranteed via finally block)
    4. Write audio data to temporary WAV file and return path

    Args:
        duration: Recording duration in seconds (default: 5)

    Returns:
        Path to temporary WAV file (16kHz, mono, 16-bit PCM)
        Caller must delete file after use with audio_file.unlink()

    Raises:
        ImportError: If PyAudio not installed (see INSTALL.md)
        RuntimeError: If microphone access fails or not available
        OSError: If temporary file cannot be created
    """
    try:
        import pyaudio
    except ImportError as e:
        raise ImportError(
            "PyAudio not installed. Install with:\n"
            "  macOS: brew install portaudio && pip install pyaudio\n"
            "  Linux: sudo apt install portaudio19-dev && pip install pyaudio\n"
            "  Windows: pip install pyaudio"
        ) from e

    # Configure audio recording (16kHz mono, 16-bit PCM for Whisper)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = None
    stream = None
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        # Record audio in chunks
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

    except OSError as e:
        raise RuntimeError(
            f"Microphone access failed. Check:\n"
            f"  1. Microphone is connected\n"
            f"  2. Permissions granted\n"
            f"  3. Not in use by another app\n"
            f"Error: {e}"
        ) from e
    finally:
        # Always clean up PyAudio resources
        if stream is not None:
            stream.stop_stream()
            stream.close()
        if audio is not None:
            audio.terminate()

    # Write to temporary WAV file
    temp_file = Path(tempfile.mktemp(suffix=".wav"))
    try:
        with wave.open(str(temp_file), "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
    except OSError as e:
        raise OSError(f"Failed to write audio file: {e}") from e

    return temp_file


def _play_audio(audio_file: Path) -> None:
    """Play audio file through system speakers.

    Loads audio using pydub (supports MP3, WAV, OGG, etc.) and plays via
    simpleaudio. Requires ffmpeg for non-WAV formats. Blocks until complete.

    Code Flow:
    1. Verify audio file exists
    2. Load audio file with pydub (auto-detects format, uses ffmpeg)
    3. Convert to raw PCM and play through simpleaudio
    4. Block until playback completes

    Args:
        audio_file: Path to audio file (MP3, WAV, OGG, etc.)

    Returns:
        None (blocks until playback finishes)

    Raises:
        ImportError: If pydub or simpleaudio not installed (see INSTALL.md)
        FileNotFoundError: If audio_file does not exist
        RuntimeError: If playback fails or format unsupported
    """
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise ImportError(
            "pydub not installed. Install with:\n"
            "  pip install pydub\n"
            "  Also install ffmpeg:\n"
            "    macOS: brew install ffmpeg\n"
            "    Linux: sudo apt install ffmpeg\n"
            "    Windows: Download from https://ffmpeg.org/"
        ) from e

    try:
        import simpleaudio as sa
    except ImportError as e:
        raise ImportError(
            "simpleaudio not installed. Install with:\n" "  pip install simpleaudio"
        ) from e

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    try:
        # Load audio (ffmpeg handles format conversion)
        audio = AudioSegment.from_file(audio_file)

        # Play audio through default output device
        playback = sa.play_buffer(
            audio.raw_data,
            num_channels=audio.channels,
            bytes_per_sample=audio.sample_width,
            sample_rate=audio.frame_rate,
        )

        # Block until playback completes
        playback.wait_done()

    except Exception as e:
        raise RuntimeError(
            f"Audio playback failed. Check:\n"
            f"  1. Audio format supported\n"
            f"  2. ffmpeg installed (for non-WAV)\n"
            f"  3. Audio device available\n"
            f"Error: {e}"
        ) from e


# Tool definitions for Claude
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_oee",
            "description": (
                "Calculate Overall Equipment Effectiveness (OEE) for a "
                "date range. Returns OEE percentage and breakdown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scrap_metrics",
            "description": (
                "Get scrap production metrics including total scrap, "
                "scrap rate, and breakdown by machine."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_quality_issues",
            "description": (
                "Get quality defect events with details about defect types, "
                "severity, and affected parts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "severity": {
                        "type": "string",
                        "description": "Optional severity filter: Low, Medium, or High",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_downtime_analysis",
            "description": (
                "Analyze downtime events including reasons, duration, "
                "and major incidents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
]


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function and return results.

    Maps tool names to their corresponding metric functions and executes them
    with the provided arguments.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Dictionary of arguments to pass to the tool

    Returns:
        Dictionary containing tool execution results or error message
    """
    if tool_name == "calculate_oee":
        return calculate_oee(**tool_args)
    elif tool_name == "get_scrap_metrics":
        return get_scrap_metrics(**tool_args)
    elif tool_name == "get_quality_issues":
        return get_quality_issues(**tool_args)
    elif tool_name == "get_downtime_analysis":
        return get_downtime_analysis(**tool_args)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


@app.command()
def setup() -> None:
    """Initialize database with synthetic data."""
    console.print(Panel.fit("🏭 Factory Operations Data Generation", style="bold blue"))

    initialize_data(days=30)

    console.print("\n✅ Setup complete! Run 'chat' to start.\n", style="bold green")


@app.command()
def chat() -> None:
    """Start interactive factory operations chatbot."""

    # Validate API key
    if not API_KEY:
        console.print(
            "❌ OPENROUTER_API_KEY not set. Please configure your .env file.",
            style="bold red",
        )
        raise typer.Exit(1)

    # Check if data exists
    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    # Load data to get date range
    data = load_data()
    start_date = data["start_date"].split("T")[0]
    end_date = data["end_date"].split("T")[0]

    # Build system prompt with context
    system_prompt = f"""You are a factory operations assistant for {FACTORY_NAME}.

You have access to 30 days of production data ({start_date} to {end_date}) covering:
- 4 machines: {', '.join([m['name'] for m in MACHINES])}
- 2 shifts: Day (6am-2pm) and Night (2pm-10pm)
- Metrics: OEE, scrap, quality issues, downtime

When answering:
1. Use tools to get accurate data
2. Provide specific numbers and percentages
3. Explain trends and patterns
4. Compare metrics when relevant
5. Be concise but thorough

Today's date is {datetime.now().strftime('%Y-%m-%d')}. When users ask about \
"today", "this week", or relative dates, calculate the appropriate date range \
based on the data available."""

    # Display welcome panel
    console.print(
        Panel.fit(
            f"🏭 {FACTORY_NAME} Operations Assistant\n\n"
            f"Data range: {start_date} to {end_date}\n"
            "Ask questions about production metrics, quality, downtime, and more.\n"
            "Type 'exit' or 'quit' to end.",
            style="bold blue",
        )
    )

    # Initialize OpenAI client (works with OpenRouter)
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

    # Conversation history
    conversation_history: List[Dict[str, Any]] = []

    # Main chat loop
    while True:
        # Get user input
        try:
            question = console.input("\n[bold green]You:[/bold green] ")
        except (KeyboardInterrupt, EOFError):
            break

        # Check for exit commands
        if question.lower().strip() in ["exit", "quit", "q"]:
            break

        # Skip empty input
        if not question.strip():
            continue

        try:
            # Build messages list
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": question})

            # Call Claude API with status indicator
            with console.status("[bold blue]Thinking...", spinner="dots"):
                response = client.chat.completions.create(
                    model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto"
                )

            # Handle tool calls in a loop
            while response.choices[0].finish_reason == "tool_calls":
                assistant_message = response.choices[0].message
                messages.append(assistant_message.model_dump())

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    result = execute_tool(tool_name, tool_args)

                    # Add tool response to messages
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(result),
                        }
                    )

                # Continue conversation with tool results
                response = client.chat.completions.create(
                    model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto"
                )

            # Extract final response
            response_text = response.choices[0].message.content

            # Update conversation history
            conversation_history = messages[1:] + [
                {"role": "assistant", "content": response_text}
            ]

            # Display assistant response
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response_text}")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

    console.print("\n👋 Goodbye!\n", style="bold blue")


@app.command()
def stats() -> None:
    """Show data statistics."""
    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    data = load_data()

    # Create statistics table
    table = Table(title=f"📊 {FACTORY_NAME} Data")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row(
        "Date Range",
        f"{data['start_date'].split('T')[0]} to {data['end_date'].split('T')[0]}",
    )
    table.add_row("Days", str(len(data["production"])))
    table.add_row("Machines", str(len(data["machines"])))
    table.add_row("Shifts", str(len(data["shifts"])))

    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
