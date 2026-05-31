# Changelog

## 0.3.0 (2026-05-30)

- Add `CLI.list_commands()` returning the registered command names
- Add `CLI.has_command(name)` checking primary names and aliases

## 0.2.0 (2026-04-29)

- Add `aliases` parameter to `@cli.command()` so commands can have shortcuts (e.g. `ls` for `list`)
- Add `type` parameter to `@option()` for casting option values to int, float, etc.
- Replace import-only stub with real test suite covering registration, dispatch, args, options, flags, aliases, and output helpers

## 0.1.10 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.9 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.6

- Add basic import test

## 0.1.5

- Add Development section to README

## 0.1.2

- Update project URLs in pyproject.toml

## 0.1.1

- Add Homepage, Changelog URLs to pyproject.toml

## 0.1.0 (2026-03-10)

- Initial release
