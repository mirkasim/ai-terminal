"""Configuration for ai-terminal.

Values can be overridden with environment variables so the tool can be
pointed at a different Ollama host or model without editing this file.
"""

import os
import platform

# Base URL of the Ollama HTTP API.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Model that translates English into shell commands.
MODEL = os.environ.get("AI_TERMINAL_MODEL", "axem-sx/boh-io")

# Seconds to wait for the model to respond.
REQUEST_TIMEOUT = float(os.environ.get("AI_TERMINAL_TIMEOUT", "60"))

# Where the interactive REPL stores command history across sessions.
HISTORY_FILE = os.environ.get(
    "AI_TERMINAL_HISTORY", os.path.expanduser("~/.ai_terminal_history")
)

# Sentinel the model returns when a request can't be expressed as a command.
UNSUPPORTED = "UNSUPPORTED"

_OS_NAME = platform.system()  # e.g. "Darwin", "Linux"

SYSTEM_PROMPT = (
    f"You are a command-line assistant running on {_OS_NAME}. "
    "Translate the user's natural-language request into a single shell command "
    "that accomplishes it on this system. "
    "Respond with ONLY the raw command on a single line. "
    "Do not add explanations, comments, markdown, code fences, or a leading "
    "prompt symbol such as '$'. "
    f"If the request cannot be fulfilled with a shell command, respond with "
    f"exactly: {UNSUPPORTED}"
)
