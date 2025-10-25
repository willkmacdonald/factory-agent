# Factory Operations Chatbot - Simplified Implementation Plan

## Project Overview

A console-based AI chatbot demo that answers factory operations questions using Claude's tool-calling capabilities via OpenRouter with synthetic manufacturing data.

### Specifications
- **Machines**: 4 production lines
- **Shifts**: 2 shifts (Day: 6am-2pm, Night: 2pm-10pm)
- **Data History**: 30 days
- **Tech Stack**: Python, Typer, Rich, OpenRouter API (Claude)

### Planted Scenarios
1. **Quality Spike**: Day 15 - elevated defects on Machine 2
2. **Machine Breakdown**: Day 22 - Machine 3 major downtime (4+ hours)
3. **Performance Improvement**: Gradual OEE increase from 65% to 80% over 30 days
4. **Shift Differences**: Night shift 5-8% lower OEE than day shift

---

## Simplified Project Structure

```
factory-agent/
├── requirements.txt          # Minimal dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── implementation-plan.md   # This file
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI entry point (~150 lines)
│   ├── config.py           # Simple settings (~10 lines)
│   ├── data.py             # Data storage & generation (~150 lines)
│   └── metrics.py          # All analysis functions (~100 lines)
└── data/
    └── production.json     # Simple JSON data storage
```

**Total Size**: ~400-500 lines of code (vs 2,000+ in original plan)

---

## Implementation PRs

### PR1: Project Setup and Simple Data Storage

**Goal**: Establish project foundation with minimal dependencies and simple data structures.

**Files to Create**:
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md` (basic)
- `src/__init__.py`
- `src/config.py`
- `src/data.py`

**Dependencies (requirements.txt)**:
```
openai>=1.51.0
typer[all]>=0.12.0
python-dotenv>=1.0.0
```

**Configuration (src/config.py)**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "anthropic/claude-3.5-sonnet"
FACTORY_NAME = "Demo Factory"
DATA_FILE = "./data/production.json"
```

**.env.example**:
```bash
# OpenRouter API Key (required)
# Get your key at https://openrouter.ai/keys
OPENROUTER_API_KEY=your-api-key-here
```

**.gitignore**:
```
# Python
__pycache__/
*.py[cod]
venv/
env/

# Environment
.env

# Data
data/

# IDE
.vscode/
.idea/
*.swp
```

**Data Storage Structure (src/data.py - Part 1)**:
```python
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import random
from pathlib import Path
from .config import DATA_FILE

# Simple in-memory data structures
MACHINES = [
    {"id": 1, "name": "CNC-001", "type": "CNC Machining Center", "ideal_cycle_time": 45},
    {"id": 2, "name": "Assembly-001", "type": "Assembly Station", "ideal_cycle_time": 120},
    {"id": 3, "name": "Packaging-001", "type": "Automated Packaging Line", "ideal_cycle_time": 30},
    {"id": 4, "name": "Testing-001", "type": "Quality Testing Station", "ideal_cycle_time": 90},
]

SHIFTS = [
    {"id": 1, "name": "Day", "start_hour": 6, "end_hour": 14},
    {"id": 2, "name": "Night", "start_hour": 14, "end_hour": 22},
]

DEFECT_TYPES = {
    "dimensional": {"severity": "High", "description": "Out of tolerance"},
    "surface": {"severity": "Medium", "description": "Surface defect"},
    "assembly": {"severity": "High", "description": "Assembly issue"},
    "material": {"severity": "Low", "description": "Material quality"},
}

DOWNTIME_REASONS = {
    "mechanical": "Mechanical failure",
    "electrical": "Electrical issue",
    "material": "Material shortage",
    "changeover": "Product changeover",
    "maintenance": "Scheduled maintenance",
}

def get_data_path() -> Path:
    """Get path to data file, creating directory if needed."""
    path = Path(DATA_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def save_data(data: Dict[str, Any]) -> None:
    """Save production data to JSON file."""
    path = get_data_path()
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_data() -> Dict[str, Any]:
    """Load production data from JSON file."""
    path = get_data_path()
    if not path.exists():
        return None
    with open(path, 'r') as f:
        return json.load(f)

def data_exists() -> bool:
    """Check if data file exists."""
    return get_data_path().exists()
```

**Testing**: Verify imports and data file operations.

**Estimated Size**: ~80 lines

---

### PR2: Simplified Data Generation with Planted Scenarios

**Goal**: Generate 30 days of simple production data with hardcoded scenarios.

**Files to Modify**:
- `src/data.py` (add generation functions)

**Implementation (src/data.py - Part 2)**:
```python
def generate_production_data(days: int = 30) -> Dict[str, Any]:
    """
    Generate simple production data with planted scenarios.

    Returns a dictionary with daily production metrics for each machine.
    """
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days - 1)

    production_data = {}

    current_date = start_date
    for day_num in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        production_data[date_str] = {}

        for machine in MACHINES:
            machine_name = machine["name"]

            # Base metrics
            base_parts = 800 + random.randint(-50, 50)

            # Scenario 3: Performance improvement over time (65% -> 80% OEE)
            improvement_factor = 1.0 + (0.23 * day_num / days)  # 23% improvement
            parts_produced = int(base_parts * improvement_factor)

            # Scenario 1: Quality spike on day 15 for Assembly-001
            if day_num == 14 and machine_name == "Assembly-001":
                scrap_rate = 0.12  # 12% defect rate (vs normal 3%)
                quality_issues = [
                    {
                        "type": "assembly",
                        "description": "Loose fastener issue - tooling calibration required",
                        "parts_affected": random.randint(5, 15),
                        "severity": "High"
                    }
                    for _ in range(4)  # Multiple incidents
                ]
            else:
                scrap_rate = 0.03  # Normal 3% defect rate
                quality_issues = []
                if random.random() < 0.15:  # 15% chance of minor issue
                    defect_type = random.choice(list(DEFECT_TYPES.keys()))
                    quality_issues = [{
                        "type": defect_type,
                        "description": DEFECT_TYPES[defect_type]["description"],
                        "parts_affected": random.randint(1, 5),
                        "severity": DEFECT_TYPES[defect_type]["severity"]
                    }]

            # Scenario 2: Major breakdown on day 22 for Packaging-001
            if day_num == 21 and machine_name == "Packaging-001":
                downtime_hours = 4.0
                downtime_events = [{
                    "reason": "mechanical",
                    "description": "Critical bearing failure requiring emergency replacement",
                    "duration_hours": 4.0
                }]
                parts_produced = int(parts_produced * 0.5)  # Major production loss
            else:
                downtime_hours = random.uniform(0.2, 0.8)  # Normal minor downtime
                downtime_events = []
                if random.random() < 0.3:  # 30% chance of logged downtime
                    reason = random.choice(list(DOWNTIME_REASONS.keys()))
                    downtime_events = [{
                        "reason": reason,
                        "description": DOWNTIME_REASONS[reason],
                        "duration_hours": round(random.uniform(0.1, 0.5), 2)
                    }]

            # Calculate derived metrics
            scrap_parts = int(parts_produced * scrap_rate)
            good_parts = parts_produced - scrap_parts

            # Scenario 4: Shift differences (night shift 5-8% lower)
            shift_metrics = {}
            for shift in SHIFTS:
                shift_name = shift["name"]
                shift_factor = 0.93 if shift_name == "Night" else 1.0
                shift_parts = int(parts_produced * 0.5 * shift_factor)
                shift_scrap = int(scrap_parts * 0.5 * shift_factor)

                shift_metrics[shift_name] = {
                    "parts_produced": shift_parts,
                    "scrap_parts": shift_scrap,
                    "good_parts": shift_parts - shift_scrap,
                    "uptime_hours": 8.0 - (downtime_hours * 0.5),
                    "downtime_hours": downtime_hours * 0.5
                }

            # Store machine data for this day
            production_data[date_str][machine_name] = {
                "parts_produced": parts_produced,
                "good_parts": good_parts,
                "scrap_parts": scrap_parts,
                "scrap_rate": round(scrap_rate * 100, 2),
                "uptime_hours": 16.0 - downtime_hours,
                "downtime_hours": downtime_hours,
                "downtime_events": downtime_events,
                "quality_issues": quality_issues,
                "shifts": shift_metrics
            }

        current_date += timedelta(days=1)

    return {
        "generated_at": datetime.now().isoformat(),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "machines": MACHINES,
        "shifts": SHIFTS,
        "production": production_data
    }

def initialize_data(days: int = 30) -> None:
    """Generate and save production data."""
    print(f"Generating {days} days of production data...")
    data = generate_production_data(days)
    save_data(data)
    print(f"✓ Generated data from {data['start_date']} to {data['end_date']}")

    # Print summary
    total_days = len(data['production'])
    print(f"✓ {total_days} days of data for {len(MACHINES)} machines")
    print(f"✓ Data saved to {DATA_FILE}")
```

**Testing**: Run generation and verify JSON output, check planted scenarios exist.

**Estimated Size**: ~150 lines

---

### PR3: Analysis Tools (Metrics Module)

**Goal**: Implement all analysis functions in a single module.

**Files to Create**:
- `src/metrics.py`

**Implementation**:
```python
from datetime import datetime
from typing import Dict, List, Any, Optional
from .data import load_data, MACHINES

def get_date_range(start_date: str, end_date: str) -> List[str]:
    """Get list of dates in range."""
    start = datetime.fromisoformat(start_date.split('T')[0])
    end = datetime.fromisoformat(end_date.split('T')[0])
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates

def calculate_oee(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate OEE metrics for date range.

    OEE = Availability × Performance × Quality
    """
    data = load_data()
    if not data:
        return {"error": "No data available"}

    dates = get_date_range(start_date, end_date)

    # Filter dates within data range
    valid_dates = [d for d in dates if d in data['production']]
    if not valid_dates:
        return {"error": "No data for specified date range"}

    # Aggregate metrics
    total_parts = 0
    total_good = 0
    total_uptime = 0
    total_planned_time = 0

    for date in valid_dates:
        day_data = data['production'][date]

        # Filter by machine if specified
        machines_to_process = [machine_name] if machine_name else day_data.keys()

        for machine in machines_to_process:
            if machine not in day_data:
                continue

            m_data = day_data[machine]
            total_parts += m_data['parts_produced']
            total_good += m_data['good_parts']
            total_uptime += m_data['uptime_hours']
            total_planned_time += 16  # 2 shifts * 8 hours

    if total_planned_time == 0:
        return {"error": "No valid data found"}

    # Calculate OEE components
    availability = total_uptime / total_planned_time if total_planned_time > 0 else 0
    quality = total_good / total_parts if total_parts > 0 else 0

    # Performance (simplified - assume running at 95% of ideal when uptime)
    performance = 0.95

    oee = availability * performance * quality

    return {
        "oee": round(oee, 3),
        "availability": round(availability, 3),
        "performance": round(performance, 3),
        "quality": round(quality, 3),
        "total_parts": total_parts,
        "good_parts": total_good,
        "scrap_parts": total_parts - total_good
    }

def get_scrap_metrics(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get scrap metrics for date range."""
    data = load_data()
    if not data:
        return {"error": "No data available"}

    dates = get_date_range(start_date, end_date)
    valid_dates = [d for d in dates if d in data['production']]

    total_scrap = 0
    total_parts = 0
    scrap_by_machine = {}

    for date in valid_dates:
        day_data = data['production'][date]
        machines_to_process = [machine_name] if machine_name else day_data.keys()

        for machine in machines_to_process:
            if machine not in day_data:
                continue

            m_data = day_data[machine]
            scrap = m_data['scrap_parts']
            parts = m_data['parts_produced']

            total_scrap += scrap
            total_parts += parts

            if not machine_name:
                scrap_by_machine[machine] = scrap_by_machine.get(machine, 0) + scrap

    scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0

    result = {
        "total_scrap": total_scrap,
        "total_parts": total_parts,
        "scrap_rate": round(scrap_rate, 2)
    }

    if scrap_by_machine:
        result["scrap_by_machine"] = scrap_by_machine

    return result

def get_quality_issues(
    start_date: str,
    end_date: str,
    severity: Optional[str] = None,
    machine_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get quality issues for date range."""
    data = load_data()
    if not data:
        return {"error": "No data available"}

    dates = get_date_range(start_date, end_date)
    valid_dates = [d for d in dates if d in data['production']]

    issues = []
    severity_breakdown = {}
    total_parts_affected = 0

    for date in valid_dates:
        day_data = data['production'][date]
        machines_to_process = [machine_name] if machine_name else day_data.keys()

        for machine in machines_to_process:
            if machine not in day_data:
                continue

            m_data = day_data[machine]
            for issue in m_data.get('quality_issues', []):
                # Filter by severity if specified
                if severity and issue['severity'] != severity:
                    continue

                issues.append({
                    "date": date,
                    "machine": machine,
                    "type": issue['type'],
                    "description": issue['description'],
                    "parts_affected": issue['parts_affected'],
                    "severity": issue['severity']
                })

                total_parts_affected += issue['parts_affected']
                sev = issue['severity']
                severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1

    return {
        "issues": issues,
        "total_issues": len(issues),
        "total_parts_affected": total_parts_affected,
        "severity_breakdown": severity_breakdown
    }

def get_downtime_analysis(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze downtime events."""
    data = load_data()
    if not data:
        return {"error": "No data available"}

    dates = get_date_range(start_date, end_date)
    valid_dates = [d for d in dates if d in data['production']]

    total_downtime = 0
    downtime_by_reason = {}
    major_events = []

    for date in valid_dates:
        day_data = data['production'][date]
        machines_to_process = [machine_name] if machine_name else day_data.keys()

        for machine in machines_to_process:
            if machine not in day_data:
                continue

            m_data = day_data[machine]
            total_downtime += m_data['downtime_hours']

            for event in m_data.get('downtime_events', []):
                reason = event['reason']
                hours = event['duration_hours']

                downtime_by_reason[reason] = downtime_by_reason.get(reason, 0) + hours

                # Track major events (> 2 hours)
                if hours > 2.0:
                    major_events.append({
                        "date": date,
                        "machine": machine,
                        "reason": reason,
                        "description": event['description'],
                        "duration_hours": hours
                    })

    return {
        "total_downtime_hours": round(total_downtime, 2),
        "downtime_by_reason": {k: round(v, 2) for k, v in downtime_by_reason.items()},
        "major_events": major_events
    }
```

**Testing**: Test each function with known date ranges and machines.

**Estimated Size**: ~180 lines

---

### PR4: CLI Interface and Claude Integration

**Goal**: Build CLI with chatbot integration.

**Files to Create**:
- `src/main.py`

**Implementation**:
```python
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openai import OpenAI
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

from .config import API_KEY, MODEL, FACTORY_NAME
from .data import initialize_data, data_exists, load_data, MACHINES
from .metrics import calculate_oee, get_scrap_metrics, get_quality_issues, get_downtime_analysis

app = typer.Typer(help="Factory Operations Chatbot - Demo Application")
console = Console()

# Tool definitions for Claude
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_oee",
            "description": "Calculate Overall Equipment Effectiveness (OEE) for a date range. Returns OEE percentage and breakdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "machine_name": {"type": "string", "description": "Optional machine name filter"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scrap_metrics",
            "description": "Get scrap production metrics including total scrap, scrap rate, and breakdown by machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "machine_name": {"type": "string", "description": "Optional machine name filter"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quality_issues",
            "description": "Get quality defect events with details about defect types, severity, and affected parts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "severity": {"type": "string", "description": "Optional severity filter: Low, Medium, or High"},
                    "machine_name": {"type": "string", "description": "Optional machine name filter"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_downtime_analysis",
            "description": "Analyze downtime events including reasons, duration, and major incidents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "machine_name": {"type": "string", "description": "Optional machine name filter"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    }
]

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool function and return results."""
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
def setup():
    """Initialize database with synthetic data."""
    console.print(Panel.fit("🏭 Factory Operations Data Generation", style="bold blue"))

    initialize_data(days=30)

    console.print("\n✅ Setup complete! Run 'chat' to start.\n", style="bold green")

@app.command()
def chat():
    """Start interactive factory operations chatbot."""

    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    # Load data to get date range
    data = load_data()
    start_date = data['start_date'].split('T')[0]
    end_date = data['end_date'].split('T')[0]

    # System prompt
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

Today's date is {datetime.now().strftime('%Y-%m-%d')}. When users ask about "today", "this week", or relative dates, calculate the appropriate date range based on the data available."""

    console.print(Panel.fit(
        f"🏭 {FACTORY_NAME} Operations Assistant\n\n"
        f"Data range: {start_date} to {end_date}\n"
        "Ask questions about production metrics, quality, downtime, and more.\n"
        "Type 'exit' or 'quit' to end.",
        style="bold blue"
    ))

    # Initialize OpenAI client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY
    )

    conversation_history = []

    while True:
        # Get user input
        try:
            question = console.input("\n[bold green]You:[/bold green] ")
        except (KeyboardInterrupt, EOFError):
            break

        if question.lower().strip() in ['exit', 'quit', 'q']:
            break

        if not question.strip():
            continue

        try:
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": question})

            # Call Claude
            with console.status("[bold blue]Thinking...", spinner="dots"):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto"
                )

            # Handle tool calls
            while response.choices[0].finish_reason == "tool_calls":
                assistant_message = response.choices[0].message
                messages.append(assistant_message.model_dump())

                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute tool
                    result = execute_tool(tool_name, tool_args)

                    # Add tool response
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(result)
                    })

                # Continue conversation
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto"
                )

            # Extract response
            response_text = response.choices[0].message.content

            # Update conversation history
            conversation_history = messages[1:] + [{"role": "assistant", "content": response_text}]

            # Show response
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response_text}")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

    console.print("\n👋 Goodbye!\n", style="bold blue")

@app.command()
def stats():
    """Show data statistics."""
    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    data = load_data()

    table = Table(title=f"📊 {FACTORY_NAME} Data")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Date Range", f"{data['start_date'].split('T')[0]} to {data['end_date'].split('T')[0]}")
    table.add_row("Days", str(len(data['production'])))
    table.add_row("Machines", str(len(data['machines'])))
    table.add_row("Shifts", str(len(data['shifts'])))

    console.print(table)
    console.print()

if __name__ == "__main__":
    app()
```

**Testing**: Manual testing of all commands.

**Estimated Size**: ~250 lines

---

## Updated README.md

```markdown
# Factory Operations Chatbot

A console-based AI chatbot demo that answers factory operations questions using Claude's tool-calling capabilities via OpenRouter with synthetic manufacturing data.

## Features

- 🤖 AI-Powered Chatbot using Claude 3.5 Sonnet via OpenRouter
- 📊 Manufacturing Metrics: OEE, scrap, quality, downtime analysis
- 🏭 30 days of synthetic factory data with interesting scenarios
- 💻 Beautiful CLI built with Typer and Rich
- 📦 Simple JSON data storage

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

## Usage

### Setup
Generate synthetic factory data:
```bash
python -m src.main setup
```

### Chat
Launch the interactive chatbot:
```bash
python -m src.main chat
```

### Stats
View data statistics:
```bash
python -m src.main stats
```

## Example Questions

- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
- "Compare day shift vs night shift performance"
- "What happened on day 22?"

## Planted Scenarios

The data includes interesting scenarios for demonstration:

1. **Quality Spike** (Day 15): Elevated defects on Assembly-001
2. **Machine Breakdown** (Day 22): 4-hour downtime on Packaging-001
3. **Performance Improvement**: OEE increases from 65% to 80% over 30 days
4. **Shift Differences**: Night shift 5-8% lower performance

## License

MIT
```

---

## Success Criteria

Each PR should meet:

✅ Code follows CLAUDE.md preferences (Python, type hints, synchronous I/O)
✅ Clear docstrings
✅ Basic error handling
✅ Manual testing verification
✅ Simple and maintainable

---

## Timeline Estimate

- PR1: 1 hour (setup & data structures)
- PR2: 1.5 hours (data generation)
- PR3: 1.5 hours (metrics)
- PR4: 2 hours (CLI & chatbot)

**Total**: ~6 hours of development (vs 24 hours in original plan)

---

## Key Simplifications from Original Plan

1. **Data Storage**: JSON files instead of SQLModel/SQLite (saves ~400 lines)
2. **Tool Consolidation**: Single metrics.py instead of 5 modules (saves ~450 lines)
3. **No Testing Infrastructure**: Manual testing only (saves ~200 lines)
4. **Simplified Generation**: Hardcoded scenarios instead of numpy/pandas (saves ~250 lines)
5. **Minimal Dependencies**: 3 instead of 10 packages
6. **Synchronous I/O**: Simpler for SQLite demos (as documented in CLAUDE.md)

**Result**: 400-500 lines instead of 2,000+ lines while maintaining all core functionality.
