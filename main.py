"""ai-terminal: type English, get and run the shell command.

Usage:
    ai-terminal "list all python files"     # one-shot
    ai-terminal                              # interactive REPL
"""

import argparse
import atexit
import os
import shlex
import subprocess
import sys

try:
    import readline  # enables history + line editing for input()
except ImportError:  # pragma: no cover - e.g. Windows without pyreadline
    readline = None

import config
from client import translate


def _init_history() -> None:
    """Load saved REPL history and arrange to persist it on exit."""
    if readline is None:
        return
    try:
        readline.read_history_file(config.HISTORY_FILE)
    except (FileNotFoundError, OSError):
        pass
    readline.set_history_length(1000)
    atexit.register(_save_history)


def _save_history() -> None:
    if readline is None:
        return
    try:
        readline.write_history_file(config.HISTORY_FILE)
    except OSError:
        pass


def _drop_last_history_entry() -> None:
    """Keep y/N confirmation answers out of the command history."""
    if readline is None:
        return
    n = readline.get_current_history_length()
    if n > 0:
        readline.remove_history_item(n - 1)


def _confirm(prompt: str) -> bool:
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    _drop_last_history_entry()
    return answer in ("y", "yes")


def _maybe_builtin(command: str) -> bool:
    """Handle 'cd' in this process so it persists. Returns True if handled.

    A 'cd' run in a subshell can't change our working directory, so we apply it
    here. Compound commands (containing &&, ||, ;, |) are left to the shell.
    """
    stripped = command.strip()
    if stripped != "cd" and not stripped.startswith("cd "):
        return False
    if any(op in stripped for op in ("&&", "||", ";", "|")):
        return False

    try:
        tokens = shlex.split(stripped)
    except ValueError:
        return False

    args = tokens[1:]
    target = args[0] if args else "~"
    if target == "-":
        target = os.environ.get("OLDPWD")
        if not target:
            print("cd: OLDPWD not set", file=sys.stderr)
            return True
        print(target)
    target = os.path.expanduser(os.path.expandvars(target))

    prev = os.getcwd()
    try:
        os.chdir(target)
    except OSError as e:
        print(f"cd: {target}: {e.strerror}", file=sys.stderr)
        return True
    os.environ["OLDPWD"] = prev
    return True


def _run_shell(command: str) -> None:
    if _maybe_builtin(command):
        return
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print()


def handle(nl_text: str, args: argparse.Namespace) -> None:
    """Translate one request and (optionally) run the resulting command."""
    nl_text = nl_text.strip()
    if not nl_text:
        return

    # Lines starting with '!' bypass the model and run directly in the shell.
    if nl_text.startswith("!"):
        command = nl_text[1:].strip()
        if command:
            _run_shell(command)
        return

    try:
        command = translate(nl_text, url=args.url, model=args.model)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return

    if command == config.UNSUPPORTED:
        print("The model could not produce a shell command for that request.", file=sys.stderr)
        return

    print(f"\n  $ {command}\n", flush=True)

    if args.dry_run:
        return

    if not args.yes and not _confirm("Run this? [y/N] "):
        print("Skipped.")
        return

    _run_shell(command)


def repl(args: argparse.Namespace) -> None:
    _init_history()
    print(
        "ai-terminal — type an English command, prefix with '!' to run a shell "
        "command directly, or 'exit' to quit."
    )
    while True:
        try:
            nl_text = input(f"ai: {os.path.basename(os.getcwd())}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if nl_text in ("exit", "quit"):
            _drop_last_history_entry()
            break
        handle(nl_text, args)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ai-terminal",
        description="Translate English into shell commands via a local Ollama model and run them.",
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="English description of the task. Omit to enter interactive mode.",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Run the generated command without asking for confirmation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated command but do not run it.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Ollama model to use (default: {config.MODEL}).",
    )
    parser.add_argument(
        "--url",
        default=None,
        help=f"Ollama base URL (default: {config.OLLAMA_URL}).",
    )
    args = parser.parse_args()

    if args.command:
        handle(" ".join(args.command), args)
    else:
        repl(args)


if __name__ == "__main__":
    main()
