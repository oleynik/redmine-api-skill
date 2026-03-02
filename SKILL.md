---
name: redmine-api
description: Work with Redmine through its REST API for issue management, status transitions, comments, journals, projects, users, and time entries. Use when tasks require reading or mutating Redmine data, building API payloads, debugging API responses, or automating Redmine workflows with curl or scripts.
---

# Redmine API
## Overview
Use this skill to execute Redmine operations through official REST endpoints with safe, repeatable request patterns.

## Follow This Workflow
1. Detect the instance's text formatting engine by running `python3 scripts/redmine_api.py detect-format`. Use the result to determine whether to write CommonMark (Markdown) or Textile in all description and notes fields.
2. Set `REDMINE_BASE_URL` (or pass `--base-url`) and confirm API connectivity/authentication first.
3. Discover IDs dynamically before updates (`project_id`, `status_id`, `tracker_id`, `activity_id`, `user_id`).
4. Read the current object state before mutating it.
5. Send JSON payloads with explicit `Content-Type: application/json` on `POST` and `PUT`.
6. Verify expected response status and then re-read the object to confirm the mutation.

## Use These Resources
- Use [references/endpoints.md](references/endpoints.md) for endpoint map, payload patterns, and status-code expectations.
- Use `scripts/redmine_api.py` for authenticated JSON requests without external Python dependencies.

## Authentication Patterns
Use one of these methods:
- `X-Redmine-API-Key` header (preferred for automation).
- HTTP Basic auth (`username:password`) when API key flow is not configured.

## Operational Guardrails
- Keep secrets out of command history where possible (prefer env vars or credential files).
- Re-resolve status and activity IDs instead of hardcoding values across environments.
- Include journals only when needed (`include=journals`) to avoid large responses.
- Use pagination on collection endpoints (`offset`, `limit`) for deterministic automation.
- Treat `422 Unprocessable Entity` as payload validation failure and inspect returned errors.
- Prefer explicit request timeouts for automation stability (`--timeout`, default 30s).

## Text Formatting
Redmine supports two markup engines: **CommonMark** (Markdown) and **Textile**. The active engine is an instance-wide setting that is not exposed via the REST API (`/settings.json` requires admin). Detection works by fetching any issue's HTML page and reading the `data-*-text-formatting-param` attribute on the edit textarea.

Run detection before composing any description or notes content:
```bash
python3 scripts/redmine_api.py detect-format
```
The command prints `common_mark` or `textile` to stdout. If no issues exist or the attribute is missing, it defaults to `common_mark` (the Redmine 5.0+ default).

### CommonMark quick reference
- Header: `## Header`
- Ordered list: `1. item`
- Unordered list: `- item`
- Inline code: `` `code` ``
- Bold: `**bold**`

### Textile quick reference
- Header: `h2. Header`
- Ordered list: `# item`
- Unordered list: `* item`
- Inline code: `@code@`
- Bold: `*bold*`

**Rule:** always detect before composing; never assume one format.

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
