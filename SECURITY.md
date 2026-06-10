# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.2.x   | Yes                |
| < 0.2   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in MIRA AdultEdge, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email the maintainer at **eidos11@naver.com** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive acknowledgment within 48 hours

## Scope

MIRA processes learner text for diagnostic analysis. Security concerns include:

- **API key exposure** — Keys should only be in `.env` (never committed)
- **Prompt injection** — Learner input could attempt to manipulate LLM behavior (Lane 3)
- **Report content safety** — Output must never contain verdict language or willpower blame (enforced by contract checks)

## Design Safeguards

- API keys are loaded from environment variables only
- Lane 1 contract checks block forbidden output patterns before delivery
- MIRA does not persist learner text locally by default. If external LLM lanes
  are enabled (`MIRA_ENABLE_LANE3=1`), learner text is sent to the configured
  provider for that call; provider-side retention and processing are governed
  by the provider's own terms and settings
- LLM calls (Lanes 2/3 extraction) are opt-in and disabled by default
