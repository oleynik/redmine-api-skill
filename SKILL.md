---
name: redmine-api
description: Work with Redmine through its REST API for issue management, status transitions, comments, journals, projects, users, and time entries. Use when tasks require reading or mutating Redmine data programmatically, building API payloads, debugging API responses, or automating Redmine workflows with curl or scripts.
---

# Redmine API

## Overview

Use this skill to execute Redmine operations through official REST endpoints with safe, repeatable request patterns.

## Follow This Workflow

1. Set `REDMINE_BASE_URL` (or pass `--base-url`) and confirm API connectivity/authentication first.
2. Discover IDs dynamically before updates (`project_id`, `status_id`, `tracker_id`, `activity_id`, `user_id`).
3. Read the current object state before mutating it.
4. Send JSON payloads with explicit `Content-Type: application/json` on `POST` and `PUT`.
5. Verify expected response status and then re-read the object to confirm the mutation.

## Use These Resources

- Use [references/endpoints.md](references/endpoints.md) for endpoint map, payload patterns, and status-code expectations.
- Use `scripts/redmine_api.py` for authenticated JSON requests without external Python dependencies.

## Authentication Patterns

Use one of these methods:

- `X-Redmine-API-Key` header (preferred for automation).
- HTTP Basic auth (`username:password`) when API key flow is not configured.

In this homelab repo, Basic auth credentials are commonly stored in `redmine.cred` and consumed by automation.

## Operational Guardrails

- Keep secrets out of command history where possible (prefer env vars or credential files).
- Re-resolve status and activity IDs instead of hardcoding values across environments.
- Include journals only when needed (`include=journals`) to avoid large responses.
- Use pagination on collection endpoints (`offset`, `limit`) for deterministic automation.
- Treat `422 Unprocessable Entity` as payload validation failure and inspect returned errors.
- Prefer explicit request timeouts for automation stability (`--timeout`, default 30s).

## Execution Patterns

### Read data

Use `GET` to list or inspect entities, then extract IDs required for write operations.

### Write data

Use `POST` for create and `PUT` for update with nested resource objects (`{"issue": {...}}`, `{"time_entry": {...}}`).

### Verify changes

Immediately query the modified object with `GET` and assert fields changed as expected.

## Done Criteria

Treat an API task as complete only when:

- request status code matches expected outcome
- response body has no validation errors
- a follow-up read confirms the intended state
