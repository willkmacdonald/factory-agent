"""Data storage and management for factory production metrics."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
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
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to save data to {path}: {e}")


def load_data() -> Optional[Dict[str, Any]]:
    """
    Load production data from JSON file.

    Returns:
        Dictionary containing production data, or None if file doesn't exist.
    """
    path = get_data_path()
    if not path.exists():
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from {path}: {e}")
    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to read data from {path}: {e}")


def data_exists() -> bool:
    """Check if data file exists."""
    return get_data_path().exists()


def generate_production_data(days: int = 30) -> Dict[str, Any]:
    """
    Generate simple production data with planted scenarios.

    Args:
        days: Number of days of data to generate (default: 30)

    Returns:
        Dictionary containing production data with planted scenarios:
        - Scenario 1: Quality spike on day 15 for Assembly-001
        - Scenario 2: Major breakdown on day 22 for Packaging-001
        - Scenario 3: Performance improvement from 65% to 80% OEE
        - Scenario 4: Night shift 5-8% lower performance
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
    """
    Generate and save production data.

    Args:
        days: Number of days of data to generate (default: 30)
    """
    print(f"Generating {days} days of production data...")
    data = generate_production_data(days)
    save_data(data)
    print(f"✓ Generated data from {data['start_date']} to {data['end_date']}")

    # Print summary
    total_days = len(data['production'])
    print(f"✓ {total_days} days of data for {len(MACHINES)} machines")
    print(f"✓ Data saved to {DATA_FILE}")
