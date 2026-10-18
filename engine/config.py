"""Settings for the Deliberation Engine. The model name is set here and nowhere else."""

from pathlib import Path

MODEL = "claude-haiku-5-5"
MAX_TOKENS = 16000
ROUND_CAP = 6
FIRST_ROUND_CHALLENGE_LIMIT = 5
LATER_ROUND_CHALLENGE_LIMIT = 3

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_CONTEXT = (PROMPTS_DIR / "system_context.md").read_text()

DEFAULT_FEATURE_REQUEST = (
    "Project managers should be able to see the full history of engagement "
    "with a country before starting a new mission."
)
