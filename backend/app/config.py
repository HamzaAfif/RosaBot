import os

from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
MODEL_NAME: str = os.getenv("ROSABOT_MODEL", "gpt-4o-mini")
TEMPERATURE: float = float(os.getenv("ROSABOT_TEMPERATURE", "0.2"))


ALLOWED_ORIGINS: list[str] = os.getenv("ROSABOT_ORIGINS", "*").split(",")


def assert_configured() -> None:
  
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to backend/.env as:\n"
            "    OPENAI_API_KEY=sk-...\n"
        )