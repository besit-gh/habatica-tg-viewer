# Habitica Companion

Telegram companion for Habitica, built with Python and aiogram 3.

## Features

- Allowlist access for a single Telegram user ID.
- Habitica profile and task browsing.
- Create, edit, complete, and delete supported tasks.
- Manual task notifications to the authorized Telegram user.
- Safe configuration through environment variables.
- Pytest, Ruff, mypy, and GitHub Actions CI.

## Quick start

See [Deployment and configuration](docs/deployment.md).

## Security

Never commit `.env`, API tokens, or Telegram bot tokens. The bot is designed for one authorized Telegram account. API errors are not automatically retried; after a timeout, refresh task state before attempting a mutation again.

## Habitica API policy

Requests identify this client through `X-Client` and are spaced to comply with Habitica API usage guidance.
