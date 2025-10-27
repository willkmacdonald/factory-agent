# Factory Operations Chatbot

A dual-interface AI demonstration system for factory operations analysis, featuring both an AI-powered chatbot and interactive web dashboard. Built with Claude's tool-calling capabilities via OpenRouter, using synthetic manufacturing data.

## Features

- **AI-Powered Chatbot** using Claude 3.5 Sonnet via OpenRouter
- **Interactive Web Dashboard** with Streamlit for visual analytics
- **Manufacturing Metrics**: OEE, scrap, quality, downtime analysis
- **30 days of synthetic factory data** with interesting planted scenarios
- **Beautiful CLI** built with Typer and Rich
- **Simple JSON data storage** (no database required)
- **Interactive natural language queries** with tool-calling
- **4 analysis tools** for accurate data retrieval
- **Visual dashboards** with Plotly charts for OEE, availability, and quality metrics

## Tech Stack

- **Python 3.11+**
- **OpenRouter API** - Claude 3.5 Sonnet with tool-calling
- **Typer** - CLI framework
- **Rich** - Beautiful terminal formatting
- **Streamlit** - Interactive web dashboard framework
- **Plotly** - Interactive data visualization
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
Generate synthetic factory data (required for both chatbot and dashboard):
```bash
python -m src.main setup
```

This creates 30 days of production data with planted scenarios and saves it to `data/production.json`.

### Chat Interface
Launch the interactive AI chatbot:
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

### Web Dashboard
Launch the interactive web dashboard:
```bash
python run_dashboard.py
```

Or directly with Streamlit:
```bash
streamlit run src/dashboard.py
```

The dashboard opens automatically in your browser at `http://localhost:8501` and provides:

- **OEE Dashboard**: Gauge chart showing current OEE percentage and trend line over 30 days
- **Availability Dashboard**: Downtime analysis by reason and major downtime events table
- **Quality Dashboard**: Scrap rate trends and quality issues with severity highlighting

Use the sidebar to filter metrics by specific machines or view all machines combined.

### Stats
View data statistics:
```bash
python -m src.main stats
```

Displays a summary table with date range, number of days, machines, and shifts.

## Example Questions (Chatbot Interface)

- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
- "Compare day shift vs night shift performance"
- "What happened on day 22?"
- "Analyze scrap rates for Assembly-001"

## Dashboard Features

The web dashboard provides three interactive tabs:

### OEE Tab
- **Gauge Chart**: Current OEE percentage with color-coded performance zones (red: 0-60%, yellow: 60-75%, green: 75-100%)
- **Trend Chart**: 30-day OEE performance trend line showing improvement over time

### Availability Tab
- **Downtime Bar Chart**: Total downtime hours aggregated by reason (changeover, maintenance, breakdown, etc.)
- **Major Events Table**: Detailed view of significant downtime events (>2 hours) including the Day 22 bearing failure

### Quality Tab
- **Scrap Rate Trend**: Daily scrap rate percentage over 30 days with area fill
- **Quality Issues Table**: Comprehensive list of defects with severity color-coding (High: red, Medium: yellow, Low: green)

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
│   ├── main.py             # CLI interface and chatbot (352 lines)
│   └── dashboard.py        # Streamlit web dashboard (226 lines)
├── data/
│   └── production.json     # Generated synthetic data
├── run_dashboard.py        # Dashboard launcher script
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies (6 packages)
├── implementation-plan.md  # Development roadmap
├── dashboards.md           # Dashboard implementation plan
└── README.md              # This file
```

**Total implementation**: ~1,100 lines across 5 core modules

## How It Works

### Core Components

1. **Data Generation** (`src/data.py`): Creates 30 days of realistic factory data with planted scenarios
2. **Metrics Engine** (`src/metrics.py`): Provides 4 analysis functions that process the data
3. **CLI Interface** (`src/main.py`): Typer-based commands with Rich formatting
4. **Web Dashboard** (`src/dashboard.py`): Streamlit app with Plotly visualizations
5. **Tool-Calling Pattern**: Claude receives tool definitions, calls them with arguments, and synthesizes responses
6. **Conversation Loop**: Maintains history and handles multi-turn tool calling

### Architecture Flow

```
Chatbot Interface:
User Question → Claude API (OpenRouter) → Tool Selection → Metrics Functions → JSON Data → Response

Dashboard Interface:
User Interaction → Streamlit UI → Metrics Functions → JSON Data → Plotly Charts
```

Both interfaces share the same underlying metrics engine and data storage, ensuring consistency.

## Development Notes

This is a demo/prototype project built following simplicity-first principles:
- **JSON files** instead of database (easier to inspect and debug)
- **Synchronous I/O** (appropriate for single-user demos)
- **No complex testing infrastructure** (manual testing sufficient)
- **Shared metrics layer** (both interfaces use the same analysis functions)
- **Streamlit for dashboards** (Python-native, zero JavaScript required)
- **~1,100 lines total** (compact and maintainable)

### Design Philosophy
- Chatbot for **exploratory analysis** and natural language queries
- Dashboard for **visual analysis** and at-a-glance metrics
- Both interfaces complement each other for comprehensive factory operations monitoring

## License

MIT
