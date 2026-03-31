# utils/env_loader.py
import os
import argparse
from dotenv import load_dotenv

def load_environment():
    """
    Parse command line for an --env argument and load environment variables.
    """
    parser = argparse.ArgumentParser(description="Run with a specific .env file.")
    parser.add_argument("--env", default=".env.dev", help="Path to the .env file to load")
    args, _ = parser.parse_known_args()

    if not os.path.exists(args.env):
        raise FileNotFoundError(f".env file not found at {args.env}")

    if not load_dotenv(dotenv_path=args.env):
        raise RuntimeError(f"Failed to load .env file at {args.env}")

