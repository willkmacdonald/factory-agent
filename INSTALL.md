# Installation Instructions

## Requirements

- **Python 3.11 or 3.12** (Python 3.13 not yet supported due to pydub compatibility)
- Git

## Standard Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd factory-agent
```

### 2. Create virtual environment
**Important**: Use Python 3.11 or 3.12 for voice interface support.

```bash
python3.12 -m venv venv  # Or python3.11
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Generate synthetic data
```bash
python -m src.main setup
```

## Voice Interface Installation

The voice interface requires additional system dependencies for audio recording.

### macOS

1. **Install PortAudio** (required for PyAudio):
   ```bash
   brew install portaudio
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API key** in `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Test the voice interface**:
   ```bash
   python -m src.main voice
   ```

### Windows

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Note: PyAudio wheels for Windows include PortAudio, so no additional installation is needed.

2. **Configure OpenAI API key** in `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

3. **Test the voice interface**:
   ```bash
   python -m src.main voice
   ```

### Linux (Debian/Ubuntu)

1. **Install system dependencies**:
   ```bash
   sudo apt install portaudio19-dev python3-pyaudio
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API key** in `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Test the voice interface**:
   ```bash
   python -m src.main voice
   ```

## Troubleshooting

### PyAudio installation fails on macOS

**Error**: `fatal error: 'portaudio.h' file not found`

**Solution**: Install PortAudio first:
```bash
brew install portaudio
pip install pyaudio
```

### PyAudio installation fails on Linux

**Error**: `error: command 'gcc' failed`

**Solution**: Install development packages:
```bash
sudo apt install portaudio19-dev python3-dev
pip install pyaudio
```

### Voice interface can't find OpenAI API key

**Error**: `❌ OPENAI_API_KEY not set`

**Solution**: Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Get your OpenAI API key at: https://platform.openai.com/api-keys

## Usage

### Console Chat (no voice dependencies required)
```bash
python -m src.main chat
```

### Voice Chat (requires voice dependencies)
```bash
python -m src.main voice
```

### Web Dashboard (requires Streamlit)
```bash
streamlit run src/dashboard.py
```

### View Statistics
```bash
python -m src.main stats
```
