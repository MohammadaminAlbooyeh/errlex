# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `ErrorSpec` model with validation for codes, HTTP statuses, and messages.
- `Registry` with deterministic ordering and duplicate-code detection.
- Python, Java, TypeScript, and Go targets backed by Jinja2 templates.
- `errlex generate`, `errlex check`, and `errlex targets` CLI commands.
- Drift detection API in `errlex.diff`.
- Golden-file tests and a CI drift gate.
- Payment service example with FastAPI and Spring Boot consumers.

## [0.1.0] - TBD

Initial planned release.
