# Factory Operations Chatbot

A console-based AI chatbot demo that answers factory operations questions using Claude's tool-calling capabilities via OpenRouter with synthetic manufacturing data.

## Implementation Status

**This is a work-in-progress demo project.** The application is not yet functional.

### Completed (PR1: Project Setup and Data Storage)
- Project structure and configuration
- Environment setup with `.env.example` and `.gitignore`
- Data storage layer (`src/data.py`) with JSON persistence
- Configuration management (`src/config.py`) for API keys and settings
- Data models for machines, shifts, defect types, and downtime reasons

### In Progress / Not Yet Implemented
- **PR2**: Data generation logic (30 days of synthetic factory metrics)
- **PR3**: Metrics calculation module (OEE, quality, downtime analysis)
- **PR4**: CLI interface with Typer and Rich
- **PR5**: OpenRouter integration and chatbot functionality

**Current state**: The foundational data structures and storage layer are in place, but you cannot yet run the application. The `setup`, `chat`, and `stats` commands described below will not work until PR2-PR4 are complete.

## Planned Features

- AI-Powered Chatbot using Claude 3.5 Sonnet via OpenRouter
- Manufacturing Metrics: OEE, scrap, quality, downtime analysis
- 30 days of synthetic factory data with interesting scenarios
- Beautiful CLI built with Typer and Rich
- Simple JSON data storage

## Tech Stack

- **Python 3.11+**
- **OpenRouter API** - Claude 3.5 Sonnet
- **Typer** - CLI framework
- **Rich** - Terminal formatting

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

## Usage (Not Yet Functional)

**Note**: These commands are planned but not yet implemented. They will be available after PR2-PR4 are complete.

### Setup (Coming in PR2)
Generate synthetic factory data:
```bash
python -m src.main setup
```

### Chat (Coming in PR4-PR5)
Launch the interactive chatbot:
```bash
python -m src.main chat
```

### Stats (Coming in PR3-PR4)
View data statistics:
```bash
python -m src.main stats
```

## Example Questions (When Complete)

Once the chatbot is implemented, you'll be able to ask questions like:

- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
- "Compare day shift vs night shift performance"
- "What happened on day 22?"

## Planned Data Scenarios

The synthetic data (to be generated in PR2) will include interesting scenarios for demonstration:

1. **Quality Spike** (Day 15): Elevated defects on Assembly-001
2. **Machine Breakdown** (Day 22): 4-hour downtime on Packaging-001
3. **Performance Improvement**: OEE increases from 65% to 80% over 30 days
4. **Shift Differences**: Night shift 5-8% lower performance

## Project Structure

```
factory-agent/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration and environment variables
│   ├── data.py            # Data storage layer and models
│   ├── generate.py        # (PR2) Data generation logic
│   ├── metrics.py         # (PR3) Metrics calculations
│   ├── main.py            # (PR4) CLI interface
│   └── chatbot.py         # (PR5) OpenRouter integration
├── data/
│   └── production.json    # (Generated) Synthetic factory data
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Development Progress

This is a hobby demo project being built incrementally. Check the `implementation-plan.md` file for detailed PR breakdown and development roadmap.

## License

MIT
