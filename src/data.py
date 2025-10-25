"""Data storage and management for factory production metrics."""
from typing import Dict, Any, Optional
import json
from pathlib import Path
from .config import DATA_FILE

# Imports for PR2 data generation (not used in PR1):
# from datetime import datetime, timedelta
# import random

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
