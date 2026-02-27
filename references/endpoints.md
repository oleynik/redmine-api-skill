# Redmine REST API Endpoints

Source docs:

- https://www.redmine.org/projects/redmine/wiki/Rest_api
- https://www.redmine.org/projects/redmine/wiki/Rest_Issues
- https://www.redmine.org/projects/redmine/wiki/Rest_TimeEntries
- https://www.redmine.org/projects/redmine/wiki/Rest_Projects
- https://www.redmine.org/projects/redmine/wiki/Rest_Users
- https://www.redmine.org/projects/redmine/wiki/Rest_Enumerations
- https://www.redmine.org/projects/redmine/wiki/Rest_Trackers
- https://www.redmine.org/projects/redmine/wiki/Rest_IssueStatuses

## Core conventions

- Base format: append `.json` (example: `/issues.json`).
- JSON envelope:
  - Create/update issue: `{"issue": {...}}`
  - Create/update time entry: `{"time_entry": {...}}`
- Common status codes:
  - `200`: successful read
  - `201`: created
  - `204`: updated/deleted with no body
  - `401`: unauthorized
  - `404`: not found
  - `422`: validation errors

## Issue lifecycle

- List issues:
  - `GET /issues.json`
  - Useful params: `project_id`, `status_id`, `assigned_to_id`, `tracker_id`, `limit`, `offset`
- Get issue:
  - `GET /issues/<id>.json`
  - Useful params: `include=journals`, `include=watchers`, `include=children`
- Create issue:
  - `POST /issues.json`
  - Example body:
    ```json
    {
      "issue": {
        "project_id": 1,
        "tracker_id": 1,
        "subject": "API-created issue",
        "description": "Created via REST API"
      }
    }
    ```
- Update issue:
  - `PUT /issues/<id>.json`
  - Example body:
    ```json
    {
      "issue": {
        "status_id": 3,
        "done_ratio": 100,
        "notes": "Closing via API"
      }
    }
    ```

## Projects, trackers, statuses, activities

- List projects: `GET /projects.json`
- List trackers: `GET /trackers.json`
- List issue statuses: `GET /issue_statuses.json`
- List time entry activities: `GET /enumerations/time_entry_activities.json`

Use these endpoints to discover IDs before create/update operations.

## Users

- Current user: `GET /users/current.json`
- List users: `GET /users.json`
- Get user by ID: `GET /users/<id>.json`

## Time entries

- List time entries:
  - `GET /time_entries.json`
  - Useful params: `issue_id`, `user_id`, `from`, `to`, `limit`, `offset`
- Create time entry:
  - `POST /time_entries.json`
  - Example body:
    ```json
    {
      "time_entry": {
        "issue_id": 26,
        "hours": 1.5,
        "activity_id": 5,
        "comments": "API worklog"
      }
    }
    ```
- Update time entry:
  - `PUT /time_entries/<id>.json`
- Delete time entry:
  - `DELETE /time_entries/<id>.json`

## Attachments

- Upload file bytes:
  - `POST /uploads.json?filename=<name>`
  - Content type: `application/octet-stream`
- Use returned upload token in a subsequent issue create/update payload under `uploads`.

## Curl template

```bash
curl -sS \
  -H "Content-Type: application/json" \
  -H "X-Redmine-API-Key: ${REDMINE_API_KEY}" \
  -X PUT \
  -d '{"issue":{"status_id":3}}' \
  "https://redmine.example.com/issues/26.json"
```

## Script templates

```bash
# Required auth + base URL (set once per shell)
export REDMINE_BASE_URL="https://redmine.example.com"
export REDMINE_API_KEY="..."

# Read with timeout and query params
python3 scripts/redmine_api.py GET /issues/26.json --query include=journals --timeout 30

# JSON write
python3 scripts/redmine_api.py PUT /issues/26.json \
  --data '{"issue":{"status_id":3,"done_ratio":100}}'

# Binary upload for attachments
python3 scripts/redmine_api.py POST /uploads.json \
  --query filename=artifact.log \
  --binary-file ./artifact.log
```
