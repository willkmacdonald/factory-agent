# Factory Operations Chatbot

A console-based AI chatbot demo that answers factory operations questions using Claude's tool-calling capabilities via OpenRouter with synthetic manufacturing data.

## Features

- AI-Powered Chatbot using Claude 3.5 Sonnet via OpenRouter
- Manufacturing Metrics: OEE, scrap, quality, downtime analysis
- 30 days of synthetic factory data with interesting scenarios
- Beautiful CLI built with Typer and Rich
- Simple JSON data storage (no database required)
- Interactive natural language queries with tool-calling
- 4 analysis tools for accurate data retrieval

## Tech Stack

- **Python 3.11+**
- **OpenRouter API** - Claude 3.5 Sonnet with tool-calling
- **Typer** - CLI framework
- **Rich** - Beautiful terminal formatting
- **OpenAI SDK** - Client library for OpenRouter API

## Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd factory-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API key**:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY from https://openrouter.ai/keys
```

## Usage

### Setup
Generate synthetic factory data:
```bash
python -m src.main setup
```

This creates 30 days of production data with planted scenarios and saves it to `data/production.json`.

### Chat
Launch the interactive chatbot:
```bash
python -m src.main chat
```

Ask questions in natural language. The chatbot uses Claude's tool-calling capabilities to retrieve accurate data.

**Example interaction**:
```
You: What was our OEE this week?
Assistant: [Uses calculate_oee tool to retrieve data and provides analysis]

You: Show me quality issues from day 15
Assistant: [Uses get_quality_issues tool and explains the quality spike]
```

Type `exit`, `quit`, or press Ctrl+C to end the chat session.

### Stats
View data statistics:
```bash
python -m src.main stats
```

Displays a summary table with date range, number of days, machines, and shifts.

## Example Questions

- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
- "Compare day shift vs night shift performance"
- "What happened on day 22?"
- "Analyze scrap rates for Assembly-001"

## Analysis Tools

The chatbot has access to 4 analysis tools:

1. **calculate_oee** - Overall Equipment Effectiveness metrics with availability, performance, and quality breakdown
2. **get_scrap_metrics** - Scrap rates and waste analysis by machine
3. **get_quality_issues** - Defect tracking with severity filtering
4. **get_downtime_analysis** - Downtime reasons, duration, and major incidents

All tools support optional machine filtering and date range selection.

## Planted Scenarios

The synthetic data includes interesting scenarios for demonstration:

1. **Quality Spike** (Day 15): Elevated defects on Assembly-001 - excellent for testing quality issue queries
2. **Machine Breakdown** (Day 22): 4-hour critical bearing failure on Packaging-001 - demonstrates downtime analysis
3. **Performance Improvement**: OEE increases from 65% to 80% over 30 days - shows trend analysis
4. **Shift Differences**: Night shift consistently 5-8% lower performance - enables shift comparison

## Project Structure

```
factory-agent/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration (11 lines)
│   ├── data.py             # Data storage and generation (217 lines)
│   ├── metrics.py          # Analysis functions (276 lines)
│   └── main.py             # CLI interface and chatbot (352 lines)
├── data/
│   └── production.json     # Generated synthetic data
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies (4 packages)
├── implementation-plan.md  # Development roadmap
└── README.md              # This file
```

**Total implementation**: ~850 lines across 4 modules

## How It Works

1. **Data Generation** (`src/data.py`): Creates 30 days of realistic factory data with planted scenarios
2. **Metrics Engine** (`src/metrics.py`): Provides 4 analysis functions that process the data
3. **CLI Interface** (`src/main.py`): Typer-based commands with Rich formatting
4. **Tool-Calling Pattern**: Claude receives tool definitions, calls them with arguments, and synthesizes responses
5. **Conversation Loop**: Maintains history and handles multi-turn tool calling

## Development Notes

This is a demo/prototype project built following simplicity-first principles:
- JSON files instead of database (easier to inspect and debug)
- Synchronous I/O (appropriate for single-user CLI demos)
- No complex testing infrastructure (manual testing)
- ~850 lines total (vs 2,000+ in initial design)

## License

MIT
