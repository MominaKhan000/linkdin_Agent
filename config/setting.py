# config/setting.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

# Load environment variables
load_dotenv(env_path)

class Settings:
    """Application settings for OpenAI"""
    
    # OpenAI API settings (Replaced Ollama)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # LinkedIn Automation
    LINKEDIN_HEADLESS = os.getenv("LINKEDIN_HEADLESS", "false").lower() == "true"
    MIN_DELAY_BETWEEN_ACTIONS = int(os.getenv("MIN_DELAY_BETWEEN_ACTIONS", 1000))
    MAX_DELAY_BETWEEN_ACTIONS = int(os.getenv("MAX_DELAY_BETWEEN_ACTIONS", 3000))
    LINKEDIN_TIMEOUT = int(os.getenv("LINKEDIN_TIMEOUT", 30000))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = project_root / "log"

# Create settings instance
settings = Settings()