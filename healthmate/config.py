import os
from pathlib import Path
from dotenv import load_dotenv


def load_env():
    """Load environment variables from the project .env file."""
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)


def get_api_key():
    """Return the first available API key for GenAI or Anthropic."""
    return os.getenv("GENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or ""
