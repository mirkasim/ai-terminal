# ai-terminal

Type what you want in plain English; ai-terminal translates it into a shell
command using a local [Ollama](https://ollama.com) model, shows it to you, and
runs it after you confirm.

```
ai> list all python files modified today
  $ find . -name '*.py' -mtime 0
Run this? [y/N]
```

Because translation happens against a model you run locally, your requests never
leave your machine.

## How it works

1. Your English request is sent to the Ollama HTTP API with a system prompt that
   asks for a single shell command (and nothing else).
2. The response is cleaned up (stray code fences, backticks, and `$` prompts are
   removed).
3. The command is printed and — unless you skip confirmation — run via your
   shell after you answer `y`.

The system prompt is OS-aware (it tells the model whether you're on macOS or
Linux), so generated commands match your platform.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for running and dependency management
- A running [Ollama](https://ollama.com) instance with a model pulled

Pull the default model (or pick your own):

```sh
ollama pull axem-sx/boh-io
```

## Running

The included script uses `uv` to install dependencies and launch the app:

```sh
# Interactive REPL
./run.sh

# One-shot command
./run.sh "show disk usage of the current directory"
```

Or invoke it directly:

```sh
uv run python main.py "list all python files"
```

## Usage

```
ai-terminal [options] [English description...]
```

Omit the description to enter the interactive REPL. In the REPL, type `exit` or
`quit` (or press Ctrl-D) to leave; command history is saved between sessions.

### Options

| Option          | Description                                                 |
| --------------- | ----------------------------------------------------------- |
| `-y`, `--yes`   | Run the generated command without asking for confirmation.  |
| `--dry-run`     | Print the generated command but do not run it.              |
| `--model MODEL` | Ollama model to use for this run.                           |
| `--url URL`     | Ollama base URL for this run.                               |

### Examples

```sh
# Print a command without running it
./run.sh --dry-run "compress the logs folder into a tarball"

# Skip the confirmation prompt
./run.sh -y "create a directory called build"

# Use a different model
./run.sh --model llama3 "find large files over 100MB"
```

## Configuration

Defaults live in [config.py](config.py) and can be overridden with environment
variables:

| Variable              | Default                  | Purpose                                   |
| --------------------- | ------------------------ | ----------------------------------------- |
| `OLLAMA_URL`          | `http://localhost:11434` | Base URL of the Ollama HTTP API.          |
| `AI_TERMINAL_MODEL`   | `axem-sx/boh-io`         | Model used to translate requests.         |
| `AI_TERMINAL_TIMEOUT` | `60`                     | Seconds to wait for the model to respond. |
| `AI_TERMINAL_HISTORY` | `~/.ai_terminal_history` | Where REPL command history is stored.     |

## Safety note

ai-terminal runs model-generated commands in your shell. Always read the printed
command before confirming, and be cautious with `-y`/`--yes`, which runs commands
without a prompt.
