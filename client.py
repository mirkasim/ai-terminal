"""Talk to Ollama: turn an English request into a shell command."""

import httpx

import config


def _clean(text: str) -> str:
    """Strip markdown/formatting the model may wrap around the command."""
    text = text.strip()

    # Remove a fenced code block: ```sh\n<cmd>\n```
    if text.startswith("```"):
        lines = text.splitlines()[1:]  # drop opening fence (and any language tag)
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Remove stray inline backticks and a leading shell prompt symbol.
    text = text.strip("`").strip()
    if text.startswith("$ "):
        text = text[2:].strip()

    return text


def translate(nl_text: str, *, url: str | None = None, model: str | None = None) -> str:
    """Return a single shell command for the given natural-language request.

    Raises RuntimeError with a human-readable message on any failure.
    """
    base = (url or config.OLLAMA_URL).rstrip("/")
    endpoint = f"{base}/api/generate"
    payload = {
        "model": model or config.MODEL,
        "system": config.SYSTEM_PROMPT,
        "prompt": nl_text,
        "stream": False,
    }

    try:
        resp = httpx.post(endpoint, json=payload, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
    except httpx.ConnectError as e:
        raise RuntimeError(f"Could not connect to Ollama at {base}. Is it running?") from e
    except httpx.TimeoutException as e:
        raise RuntimeError(f"Ollama timed out after {config.REQUEST_TIMEOUT:g}s.") from e
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Ollama returned {e.response.status_code}: {e.response.text.strip()}"
        ) from e
    except httpx.HTTPError as e:
        raise RuntimeError(f"Request to Ollama failed: {e}") from e

    command = _clean(resp.json().get("response", ""))
    if not command:
        raise RuntimeError("Ollama returned an empty response.")
    return command
