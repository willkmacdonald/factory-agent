# Voice Interface Implementation Plan

## Overview
Add a cross-platform voice interface to the factory agent chatbot, enabling users to ask questions verbally and receive spoken responses. Uses OpenAI Whisper (speech-to-text) and TTS APIs for premium quality audio.

## User Flow
```
$ python -m src.main voice

🎤 Voice Chat Mode

Press Enter to record (5 seconds)
Type 'exit' to quit

[Press Enter]
🎤 Recording... (5 seconds)
⏳ Transcribing...
You said: "What was our OEE this week?"

⏳ Assistant is thinking...
Assistant: "The OEE for this week was 78.5%..."
🔊 [Audio plays while text shows]

[Press Enter for next question...]
```

## Technical Architecture

### Components
1. **Audio Recording**: PyAudio (cross-platform) → 16kHz mono WAV
2. **Speech-to-Text**: OpenAI Whisper API
3. **Chat Logic**: Reuses existing Claude conversation loop with tool calling
4. **Text-to-Speech**: OpenAI TTS API → MP3
5. **Audio Playback**: pydub + simpleaudio (cross-platform)

### Dependencies
- `pyaudio>=0.2.13` - Cross-platform audio recording
- `pydub>=0.25.1` - Audio file handling and conversion
- `simpleaudio>=1.0.4` - Simple cross-platform audio playback

### Configuration
- `TTS_VOICE = "alloy"` (options: alloy, echo, fable, onyx, nova, shimmer)
- `TTS_MODEL = "tts-1"`
- `WHISPER_MODEL = "whisper-1"`
- `RECORDING_DURATION = 5` (seconds)

## Implementation - PR-Sized Chunks

### PR #1: Dependencies and Configuration Setup ✅ COMPLETED
**Status**: Merged (commit `cbeefdc`)
**Size**: ~10 lines | **Risk**: Low | **Testable**: Yes

**Files Modified**:
- `requirements.txt`
- `src/config.py`

**Changes**:
1. Add 3 audio dependencies to requirements.txt:
   ```
   pyaudio>=0.2.13
   pydub>=0.25.1
   simpleaudio>=1.0.4
   ```

2. Add 4 voice configuration constants to src/config.py:
   ```python
   # Voice interface settings
   TTS_VOICE = "alloy"  # OpenAI voice: alloy, echo, fable, onyx, nova, shimmer
   TTS_MODEL = "tts-1"  # or "tts-1-hd" for higher quality
   WHISPER_MODEL = "whisper-1"
   RECORDING_DURATION = 5  # seconds
   ```

**Testing**:
```bash
pip install -r requirements.txt
python -c "import pyaudio; import pydub; import simpleaudio; print('✓ All imports successful')"
```

**Commit Message**: "Add voice interface dependencies and configuration"

---

### PR #2: Audio Recording and Playback Utilities ✅ COMPLETED
**Status**: Merged and Simplified (commit `0216939`, then `ddf56dd`)
**Size**: ~156 lines (simplified from original) | **Risk**: Low | **Testable**: Yes

**Files Modified**:
- `src/main.py`

**Changes**:
Add two cross-platform helper functions at module level:

```python
def _record_audio(duration: int = 5) -> Path:
    """Record audio using PyAudio (cross-platform).

    Args:
        duration: Recording duration in seconds

    Returns:
        Path to temporary WAV file
    """
    import pyaudio
    import wave

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Whisper-optimized

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save to temp file
    temp_file = Path(tempfile.mktemp(suffix=".wav"))
    with wave.open(str(temp_file), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return temp_file


def _play_audio(audio_file: Path) -> None:
    """Play audio file using simpleaudio (cross-platform).

    Args:
        audio_file: Path to MP3 or WAV file
    """
    from pydub import AudioSegment
    import simpleaudio as sa

    # Load audio (handles MP3, WAV, etc.)
    audio = AudioSegment.from_file(audio_file)

    # Convert to WAV in memory
    playback = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )

    # Wait for playback to finish
    playback.wait_done()
```

**Testing**:
Add temporary test command to verify recording/playback:
```python
@app.command()
def test_audio() -> None:
    """Test audio recording and playback."""
    console.print("Recording 5 seconds...", style="yellow")
    audio_file = _record_audio(5)
    console.print(f"Saved to {audio_file}", style="green")
    console.print("Playing back...", style="yellow")
    _play_audio(audio_file)
    audio_file.unlink()
    console.print("✓ Test complete", style="green")
```

Run: `python -m src.main test-audio`

**Commit Message**: "Add cross-platform audio recording and playback utilities"

---

### PR #3: Extract Shared Chat Logic ✅ COMPLETED & MERGED
**Status**: Merged (commit `5185621`)
**Size**: +217 lines, -9 lines | **Risk**: Low | **Testable**: Yes
**Review Scores**: Simplicity 9.5/10, CLAUDE.md Compliance 98/100

**Files Modified**:
- `src/main.py` (+52 lines, -9 lines)
- `tests/test_main.py` (+174 lines, new file)

**Actual Implementation** (differs from initial plan):
Three extracted functions with enhanced docstrings and fixed conversation history:

```python
def _build_system_prompt() -> str:
    """Build system prompt with factory context and tool definitions.

    Includes detailed "Code Flow" section explaining the process.
    """
    # Loads data, builds machine list, constructs prompt with factory context
    # See src/main.py:195-236 for full implementation

def _get_chat_response(
    client: OpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Get Claude response with tool calling support.

    **KEY FIX**: Returns Tuple[response_text, new_history] to preserve tool calls
    in conversation history (fixes bug where tool context was lost).

    Includes detailed "Code Flow" section with step-by-step loop explanation.
    """
    # Builds messages, enters tool-calling loop, returns response + full history
    # See src/main.py:239-320 for full implementation

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool function and return results.

    Maps tool names to metric functions via simple if/elif chain.
    """
    # Routes to: calculate_oee, get_scrap_metrics, get_quality_issues, get_downtime_analysis
    # See src/main.py:444-477 for full implementation
```

**Key Improvements** (vs original plan):
1. **Fixed conversation history bug**: `_get_chat_response()` now returns `Tuple[str, List]` with full history including tool calls
2. **Enhanced docstrings**: Added detailed "Code Flow" sections (total ~100 lines of documentation)
3. **Type hint consistency**: Uses `Tuple` from typing module throughout
4. **Demo-appropriate tests**: Created 6 focused smoke tests (175 lines) instead of exhaustive suite

Refactored `chat()` command now uses extracted functions:

```python
# In chat() command (src/main.py:480-552):

# Build system prompt using extracted function
system_prompt = _build_system_prompt()

# Get response using shared logic
response_text, new_history = _get_chat_response(
    client, system_prompt, conversation_history, question
)

# Update history with ALL new messages (includes tool calls)
conversation_history.extend(new_history)
```

**Testing**:
```bash
# Run all tests (including 6 new smoke tests for extracted functions)
python -m pytest tests/ -v

# Results: 9/9 tests passing
# - 3 tests from test_config.py (existing)
# - 6 tests from test_main.py (new smoke tests)
# - 100% coverage of PR #3 extracted functions
```

**Commit Message**: "PR #3: Extract shared chat logic with fixes"

---

### PR #4: Voice Command Implementation
**Size**: ~65 lines | **Risk**: Low | **Testable**: Yes

**Files Modified**:
- `src/main.py`

**Changes**:
Add new `voice()` command:

```python
@app.command()
def voice() -> None:
    """Start voice chat with factory assistant.

    Uses OpenAI Whisper for speech-to-text and TTS for text-to-speech.
    Press Enter to record 5 seconds of audio, then get spoken response.
    """

    if not API_KEY:
        console.print("❌ OpenRouter API key not set", style="bold red")
        raise typer.Exit(1)

    # Check for OpenAI API key (needed for Whisper/TTS)
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        console.print("❌ OPENAI_API_KEY not set (needed for Whisper/TTS)", style="bold red")
        raise typer.Exit(1)

    # Initialize clients
    openrouter_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    openai_client = OpenAI(api_key=openai_key)

    # Build system prompt
    system_prompt = _build_system_prompt()
    conversation_history = []

    # Welcome message
    console.print(Panel.fit(
        "[bold blue]🎤 Voice Chat Mode[/bold blue]\n\n"
        "Press Enter to record (5 seconds)\n"
        "Type 'exit' to quit",
        border_style="blue"
    ))

    # Voice chat loop
    while True:
        try:
            # Wait for Enter or exit command
            cmd = input("\n[Press Enter to record, or type 'exit']: ").strip()

            if cmd.lower() in ["exit", "quit"]:
                console.print("\n👋 Goodbye!", style="bold blue")
                break

            # Record audio
            console.print("🎤 Recording... (5 seconds)", style="yellow")
            audio_file = _record_audio(duration=RECORDING_DURATION)

            # Transcribe with Whisper
            with console.status("⏳ Transcribing..."):
                with open(audio_file, "rb") as f:
                    transcript = openai_client.audio.transcriptions.create(
                        model=WHISPER_MODEL,
                        file=f
                    )
                transcribed_text = transcript.text

            console.print(f"[bold green]You said:[/bold green] {transcribed_text}")

            # Get Claude response using shared logic
            with console.status("⏳ Assistant is thinking..."):
                response_text = _get_chat_response(
                    openrouter_client,
                    system_prompt,
                    conversation_history,
                    transcribed_text
                )

            # Display text response
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response_text}")

            # Generate speech with TTS
            with console.status("🔊 Generating speech..."):
                tts_file = Path(tempfile.mktemp(suffix=".mp3"))
                tts_response = openai_client.audio.speech.create(
                    model=TTS_MODEL,
                    voice=TTS_VOICE,
                    input=response_text
                )
                tts_response.stream_to_file(tts_file)

            # Play audio
            _play_audio(tts_file)

            # Update conversation history
            conversation_history.append({"role": "user", "content": transcribed_text})
            conversation_history.append({"role": "assistant", "content": response_text})

            # Cleanup temp files
            audio_file.unlink()
            tts_file.unlink()

        except KeyboardInterrupt:
            console.print("\n\n👋 Goodbye!", style="bold blue")
            break
        except Exception as e:
            console.print(f"\n❌ Error: {e}", style="bold red")
```

**Testing**:
```bash
python -m src.main voice
# Test several voice questions
# Verify audio quality and conversation flow
```

**Commit Message**: "Add voice command for audio-based chat interactions"

---

### PR #5: Documentation Updates
**Size**: ~50 lines | **Risk**: None | **Testable**: Manual review

**Files Modified**:
- `README.md`

**Changes**:
Add voice interface section to README.md after "Chat Interface" section:

```markdown
### Voice Interface
Launch the voice-based chatbot:
```bash
python -m src.main voice
```

The voice interface provides the same functionality as the text chat, but with audio input/output:

- Press Enter to record your question (5 seconds)
- Whisper API transcribes your speech to text
- Claude processes your question using the same tool-calling logic
- TTS API generates natural-sounding speech response
- Audio plays while text is displayed

**Requirements**:
- OpenAI API key (set `OPENAI_API_KEY` in `.env`)
- Working microphone
- Audio output (speakers/headphones)

**Installation Notes**:
- **macOS**: `brew install portaudio && pip install -r requirements.txt`
- **Windows**: `pip install -r requirements.txt` (PyAudio wheel includes PortAudio)

**Cost Estimates** (OpenAI APIs):
- Whisper: $0.006/minute of audio
- TTS: $15 per 1M characters (~$0.015 per typical response)
- Typical demo session (20 questions): ~$0.50

**Example Voice Questions**:
Same as text chat:
- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
```

**Testing**:
- Manual review of documentation
- Verify all instructions are accurate
- Check formatting renders correctly

**Commit Message**: "Document voice interface usage and implementation"

---

## Summary

### Total Implementation
- **5 PRs**: Sequential implementation
- **~220 lines total**: Including documentation
- **Estimated time**: 2.5 hours
- **Risk level**: Low (each PR independently testable)

### Testing Strategy
1. **PR #1**: ✅ Verify imports work on both platforms (Completed)
2. **PR #2**: ✅ Manual test recording/playback (Completed)
3. **PR #3**: ✅ Automated tests + code reviews (9/9 tests passing, Completed & Merged)
4. **PR #4**: End-to-end voice workflow test (Next)
5. **PR #5**: Documentation review (Next)

### Dependencies Installation

**macOS**:
```bash
brew install portaudio
pip install -r requirements.txt
```

**Windows**:
```bash
pip install -r requirements.txt
```

### Cost Estimates
- **Whisper**: $0.006/min → ~$0.12 for 20 questions
- **TTS**: $15/1M chars → ~$0.30 for 20 responses
- **Total**: ~$0.50 per demo session

### Rollback Plan
Each PR is independently revertible:
- PR #1: ✅ Merged - Remove dependencies, no functional impact
- PR #2: ✅ Merged - Remove unused helper functions
- PR #3: ✅ Merged (5185621) - Revert to inline chat() implementation (would need to update tests)
- PR #4: Not yet implemented - Remove voice command
- PR #5: Not yet implemented - Revert documentation

### Current Status (2025-10-27)
- ✅ **PR #1**: Dependencies and configuration (Merged: commit `cbeefdc`)
- ✅ **PR #2**: Audio utilities (Merged: commits `0216939`, `ddf56dd`)
- ✅ **PR #3**: Extract shared chat logic (Merged: commit `5185621`)
- ⏳ **PR #4**: Voice command implementation (NEXT - Ready to start)
- ⏳ **PR #5**: Documentation updates (After PR #4)

### Future Enhancements (Out of Scope)
- Variable recording duration
- Voice activation detection
- Multiple language support
- Conversation export with audio
- Streaming TTS for faster response
