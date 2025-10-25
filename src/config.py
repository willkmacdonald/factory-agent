"""Configuration settings for the factory operations chatbot."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
FACTORY_NAME: str = os.getenv("FACTORY_NAME", "Demo Factory")
DATA_FILE: str = os.getenv("DATA_FILE", "./data/production.json")
