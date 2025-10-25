"""Configuration settings for the factory operations chatbot."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
MODEL: str = "anthropic/claude-3.5-sonnet"
FACTORY_NAME: str = "Demo Factory"
DATA_FILE: str = "./data/production.json"
