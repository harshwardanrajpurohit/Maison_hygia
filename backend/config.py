import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


class Settings:
    # LLM Settings (OpenAI only)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

    # Token Limits
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "4096"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "800"))
    MAX_RETRIEVAL_CHUNKS: int = int(os.getenv("MAX_RETRIEVAL_CHUNKS", "5"))
    MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "3"))

    # Memory Limits
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

    # Language Intelligence
    LANGUAGE_DETECTION_ENABLED: bool = os.getenv("LANGUAGE_DETECTION_ENABLED", "true").lower() == "true"


settings = Settings()
