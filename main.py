"""Run one deliberation: python main.py [--request "..." | --request-file path]"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from engine.agents import AgentReplyError, AnthropicClient
from engine.config import DEFAULT_FEATURE_REQUEST
from engine.deliberation import run_deliberation


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Deliberate on a vague feature request for the Government CRM.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--request", help="the Feature Request text")
    source.add_argument("--request-file", type=Path, help="a file containing the Feature Request")
    args = parser.parse_args(argv)

    if args.request is not None:
        feature_request = args.request.strip()
    elif args.request_file is not None:
        feature_request = args.request_file.read_text().strip()
    else:
        feature_request = DEFAULT_FEATURE_REQUEST
    if not feature_request:
        parser.error("the Feature Request is empty")

    load_dotenv()
    try:
        result = run_deliberation(feature_request, AnthropicClient())
    except AgentReplyError as error:
        sys.exit(f"Run stopped: {error}. Trace so far saved to {error.run_dir}")
    print(f"Stop reason: {result.stop_reason}. Saved to {result.run_dir}")


if __name__ == "__main__":
    main()
