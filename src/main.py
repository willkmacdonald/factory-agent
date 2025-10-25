"""
Factory Operations Chatbot - CLI Interface

This module provides the main CLI interface for the factory operations chatbot.
It handles user interaction, Claude API integration, and tool execution.
"""

from datetime import datetime
from typing import Any, Dict, List
import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openai import OpenAI

from .config import API_KEY, MODEL, FACTORY_NAME
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
    console.print(
        Panel.fit("🏭 Factory Operations Data Generation", style="bold blue")
    )

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
        console.print(
            "❌ Data not found. Please run 'setup' first.", style="bold red"
        )
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
        console.print(
            "❌ Data not found. Please run 'setup' first.", style="bold red"
        )
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
