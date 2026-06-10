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
- No user data is stored or transmitted beyond the current session
- LLM calls (Lane 3) are optional and can be disabled entirely
