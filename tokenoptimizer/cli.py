#!/usr/bin/env python3
"""Command-line interface for Token Optimizer."""

import argparse
import sys
from typing import NoReturn

from . import __version__
from .client import (
    TokenOptimizerClient,
    AuthenticationError,
    APIError,
    CompressionResult,
)
from .config import (
    load_api_key,
    save_api_key,
    delete_api_key,
    get_config_path,
    ENV_VAR_NAME,
)

# Aggressiveness presets
PRESETS = {
    "light": 0.2,
    "moderate": 0.5,
    "aggressive": 0.8,
}


def error(message: str, code: int = 1) -> NoReturn:
    """Print error message and exit."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def print_stats(result: CompressionResult, quiet: bool = False) -> None:
    """Print compression statistics to stderr."""
    if quiet:
        return
    print(
        f"[{result.original_input_tokens} -> {result.output_tokens} tokens "
        f"({result.tokens_saved} saved, {result.compression_ratio:.1f}% reduction) "
        f"in {result.compression_time:.2f}s]",
        file=sys.stderr,
    )


def cmd_auth(args: argparse.Namespace) -> int:
    """Handle the auth subcommand."""
    if args.auth_action == "set":
        if args.key:
            api_key = args.key
        else:
            print("Enter your API key: ", end="", file=sys.stderr)
            api_key = input().strip()

        if not api_key:
            error("API key cannot be empty")

        save_api_key(api_key)
        print(f"API key saved to {get_config_path()}", file=sys.stderr)
        return 0

    elif args.auth_action == "show":
        api_key = load_api_key()
        if api_key:
            # Mask the key for security
            if len(api_key) > 8:
                masked = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
            else:
                masked = "*" * len(api_key)
            print(f"API key: {masked}")
            print(f"Source: {'environment' if ENV_VAR_NAME in __import__('os').environ else 'config file'}")
        else:
            print("No API key configured")
            print(f"Set one with: tokenoptimizer auth set")
            print(f"Or set {ENV_VAR_NAME} environment variable")
        return 0

    elif args.auth_action == "delete":
        if delete_api_key():
            print("API key deleted", file=sys.stderr)
        else:
            print("No stored API key found", file=sys.stderr)
        return 0

    elif args.auth_action == "path":
        print(get_config_path())
        return 0

    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    """Handle the optimize command (default)."""
    api_key = load_api_key()
    if not api_key:
        error(
            f"No API key configured. Run 'tokenoptimizer auth set' or set {ENV_VAR_NAME}"
        )

    # Get input text
    if args.prompt:
        text = " ".join(args.prompt)
    elif args.file:
        try:
            with open(args.file, "r") as f:
                text = f.read()
        except FileNotFoundError:
            error(f"File not found: {args.file}")
        except IOError as e:
            error(f"Failed to read file: {e}")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        error("No input provided. Use --prompt, --file, or pipe via stdin")

    if not text.strip():
        error("Input text is empty")

    # Determine aggressiveness
    aggressiveness = args.aggressiveness
    if args.light:
        aggressiveness = PRESETS["light"]
    elif args.moderate:
        aggressiveness = PRESETS["moderate"]
    elif args.aggressive:
        aggressiveness = PRESETS["aggressive"]

    # Create client and compress
    client = TokenOptimizerClient(api_key, timeout=args.timeout)

    try:
        result = client.compress(
            text=text,
            aggressiveness=aggressiveness,
            max_output_tokens=args.max_tokens,
            min_output_tokens=args.min_tokens,
        )
    except AuthenticationError as e:
        error(f"Authentication failed: {e}")
    except APIError as e:
        error(str(e))
    except ValueError as e:
        error(str(e))

    # Output
    if args.stats_only:
        print(f"Original tokens: {result.original_input_tokens}")
        print(f"Output tokens: {result.output_tokens}")
        print(f"Tokens saved: {result.tokens_saved}")
        print(f"Compression ratio: {result.compression_ratio:.1f}%")
        print(f"Compression time: {result.compression_time:.2f}s")
    else:
        print_stats(result, quiet=args.quiet)
        print(result.output)

    return 0


def create_auth_parser() -> argparse.ArgumentParser:
    """Create the auth subcommand parser."""
    parser = argparse.ArgumentParser(
        prog="tokenoptimizer auth",
        description="Manage API key for The Token Company API",
    )
    subparsers = parser.add_subparsers(
        dest="auth_action",
        metavar="action",
    )

    # auth set
    auth_set = subparsers.add_parser(
        "set",
        help="Set API key",
        description="Save your API key to the config file",
    )
    auth_set.add_argument(
        "--key", "-k",
        help="API key (will prompt if not provided)",
    )

    # auth show
    subparsers.add_parser(
        "show",
        help="Show current API key status",
        description="Display information about the configured API key",
    )

    # auth delete
    subparsers.add_parser(
        "delete",
        help="Delete stored API key",
        description="Remove the API key from the config file",
    )

    # auth path
    subparsers.add_parser(
        "path",
        help="Show config file path",
        description="Print the path to the config file",
    )

    return parser


def create_optimize_parser() -> argparse.ArgumentParser:
    """Create the main optimize parser."""
    parser = argparse.ArgumentParser(
        prog="tokenoptimizer",
        description="Optimize tokens using The Token Company API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tokenoptimizer "Your prompt here"
  echo "Your prompt" | tokenoptimizer
  tokenoptimizer --file prompt.txt
  tokenoptimizer --aggressive "Your prompt"
  tokenoptimizer -a 0.8 "Your prompt"
  tokenoptimizer auth set
  tokenoptimizer auth set --key YOUR_API_KEY

Aggressiveness levels:
  --light       0.2 - Preserves content safely
  --moderate    0.5 - Balances compression with quality (default)
  --aggressive  0.8 - Maximizes token reduction

Environment variables:
  TOKENOPTIMIZER_API_KEY    API key (overrides config file)
""",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"tokenoptimizer {__version__}",
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        default=[],
        help="Prompt text to optimize",
    )

    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Read prompt from file",
    )

    # Aggressiveness options
    agg_group = parser.add_mutually_exclusive_group()
    agg_group.add_argument(
        "--aggressiveness", "-a",
        type=float,
        default=0.5,
        metavar="LEVEL",
        help="Compression aggressiveness 0.0-1.0 (default: 0.5)",
    )
    agg_group.add_argument(
        "--light", "-l",
        action="store_true",
        help="Light compression (aggressiveness=0.2)",
    )
    agg_group.add_argument(
        "--moderate", "-m",
        action="store_true",
        help="Moderate compression (aggressiveness=0.5)",
    )
    agg_group.add_argument(
        "--aggressive", "-A",
        action="store_true",
        help="Aggressive compression (aggressiveness=0.8)",
    )

    # Token limits
    parser.add_argument(
        "--max-tokens",
        type=int,
        metavar="N",
        help="Maximum output tokens",
    )
    parser.add_argument(
        "--min-tokens",
        type=int,
        metavar="N",
        help="Minimum output tokens",
    )

    # Output options
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress statistics output",
    )
    parser.add_argument(
        "--stats-only", "-s",
        action="store_true",
        help="Only show statistics, not the optimized text",
    )

    # Other options
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 60)",
    )

    return parser


def main() -> int:
    """Main entry point."""
    # Check if first arg is 'auth' subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        parser = create_auth_parser()
        args = parser.parse_args(sys.argv[2:])
        if not args.auth_action:
            parser.print_help()
            return 1
        return cmd_auth(args)
    else:
        parser = create_optimize_parser()
        args = parser.parse_args()
        return cmd_optimize(args)


if __name__ == "__main__":
    sys.exit(main())
