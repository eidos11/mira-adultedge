"""Lane 2 — Prolog-based formal verification runner."""

# Pre-import pyswip at package load time so it's cached in sys.modules
# before any lazy import inside bridge.py's _query_prolog(). Without this,
# uv's environment isolation can cause ModuleNotFoundError on lazy import
# after a Codex CLI subprocess call.
try:
    import pyswip as _pyswip  # noqa: F401
except ImportError:
    pass
