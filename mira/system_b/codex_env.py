"""Environment hygiene for Codex CLI subprocesses (Lane 2 + Lane 3).

Codex authenticates via the ChatGPT subscription (OAuth / keychain). If
``OPENAI_API_KEY`` is present in the environment, codex can silently switch to
API-key auth — which manifests as mixed-auth stalls, 120s timeouts, or empty
extraction (``return []``), and incurs unintended per-token API billing.

A codex subprocess that inherits the parent environment unchanged is therefore
exposed to whatever ``OPENAI_API_KEY`` happens to be set (a past global export,
or an ``apienv``-style shell that sets keys for the OpenAI/Anthropic fallback
paths). Stripping the key from the subprocess environment guarantees
subscription mode regardless of the ambient shell — the code-level equivalent of
the ``env -u OPENAI_API_KEY codex ...`` discipline (ops governance §6).
"""

from __future__ import annotations

import os


def codex_subprocess_env() -> dict[str, str]:
    """Return a copy of the current environment with ``OPENAI_API_KEY`` removed.

    Pass as ``subprocess.run(..., env=codex_subprocess_env())`` for every codex
    CLI call so codex always uses the ChatGPT subscription, never an ambient API
    key. All other variables (PATH, HOME, codex config, etc.) are preserved.
    """
    return {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
