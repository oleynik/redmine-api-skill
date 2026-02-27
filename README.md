# redmine-api

Portable Redmine API skill and helper script for issue workflows, status transitions, journals, users, projects, and time entries.

## What this repo includes

- `SKILL.md`: skill behavior and workflow guidance.
- `references/endpoints.md`: Redmine endpoint map and payload patterns.
- `scripts/redmine_api.py`: dependency-free Python CLI for authenticated Redmine REST calls.
- `agents/openai.yaml`: agent interface metadata.

## Requirements

- Python 3.9+ (tested with system `python3`)
- Access to a Redmine instance with REST API enabled
- Authentication via API key or HTTP Basic credentials

## Quick start

1. Create a local `.env` file (auto-loaded by `scripts/redmine_api.py`):

```bash
cat > .env <<'EOF'
REDMINE_BASE_URL=https://redmine.example.com
REDMINE_API_KEY=your_api_key
# Optional for basic auth instead of API key:
# REDMINE_USER=username
# REDMINE_PASSWORD=password
EOF
```

2. Alternative: export variables in your shell:

```bash
export REDMINE_BASE_URL="https://redmine.example.com"
export REDMINE_API_KEY="your_api_key"
```

3. Make a request:

```bash
python3 scripts/redmine_api.py GET /issue_statuses.json
```

## Script usage

```bash
python3 scripts/redmine_api.py {GET,POST,PUT,DELETE} /path.json [options]
```

Common options:

- `--base-url`: required unless `REDMINE_BASE_URL` is set
- `--api-key`: API key (or `REDMINE_API_KEY`)
- `--cred-file`: file containing `username:password`
- `--basic-user`, `--basic-password`: basic auth creds (or env vars)
- `--query key=value`: repeatable query parameters
- `--data` / `--data-file`: JSON request body
- `--binary-file`: raw body bytes (for uploads)
- `--content-type`: content type for `--binary-file` (default `application/octet-stream`)
- `--timeout`: request timeout in seconds (default `30`)
- `--insecure`: disable TLS certificate verification

## Examples

Get issue with journals:

```bash
python3 scripts/redmine_api.py GET /issues/26.json --query include=journals
```

Update issue status:

```bash
python3 scripts/redmine_api.py PUT /issues/26.json \
  --data '{"issue":{"status_id":3,"done_ratio":100}}'
```

Create time entry:

```bash
python3 scripts/redmine_api.py POST /time_entries.json \
  --data '{"time_entry":{"issue_id":26,"hours":1.5,"activity_id":5,"comments":"API worklog"}}'
```

Upload attachment bytes:

```bash
python3 scripts/redmine_api.py POST /uploads.json \
  --query filename=artifact.log \
  --binary-file ./artifact.log
```

## Notes

- The script fails fast if base URL or authentication is missing.
- A `.env` file in the current working directory is loaded automatically.
- For write operations, follow a read-before-write and read-after-write verification pattern.
- Redmine validation errors are typically returned as HTTP `422`.
