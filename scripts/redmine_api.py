#!/usr/bin/env python3
"""
Minimal Redmine REST client for JSON endpoints.

Examples:
  python3 scripts/redmine_api.py GET /issue_statuses.json --base-url https://redmine.example.com --api-key "$REDMINE_API_KEY"
  python3 scripts/redmine_api.py GET /issues/26.json --base-url https://redmine.example.com --query include=journals --cred-file redmine.cred
  python3 scripts/redmine_api.py PUT /issues/26.json --base-url https://redmine.example.com --data '{"issue":{"status_id":3}}' --api-key "$REDMINE_API_KEY"
  python3 scripts/redmine_api.py POST /uploads.json --base-url https://redmine.example.com --query filename=log.txt --binary-file ./log.txt --api-key "$REDMINE_API_KEY"
"""

import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request


def load_dotenv(path=".env"):
    def parse_value(raw):
        raw = raw.strip()
        if not raw:
            return ""

        if raw[0] in ('"', "'"):
            quote = raw[0]
            idx = 1
            while idx < len(raw):
                if raw[idx] == quote and raw[idx - 1] != "\\":
                    return raw[1:idx].replace(f"\\{quote}", quote)
                idx += 1
            return raw[1:]

        comment_idx = raw.find(" #")
        if comment_idx != -1:
            raw = raw[:comment_idx]
        return raw.rstrip()

    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export ") :].strip()
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                os.environ.setdefault(key, parse_value(value))
    except FileNotFoundError:
        return


def parse_query(items):
    parsed = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid query parameter '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        parsed.append((key, value))
    return parsed


def build_headers(args):
    headers = {
        "Accept": "application/json",
        "User-Agent": args.user_agent or os.getenv("REDMINE_USER_AGENT", "curl/8.7.1"),
    }

    api_key = args.api_key or os.getenv("REDMINE_API_KEY")
    if api_key:
        headers["X-Redmine-API-Key"] = api_key
        return headers

    if args.cred_file:
        with open(args.cred_file, "r", encoding="utf-8") as fh:
            creds = fh.read().strip()
        if ":" not in creds:
            raise ValueError("Credential file must contain username:password.")
        encoded = base64.b64encode(creds.encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {encoded}"
        return headers

    user = args.basic_user or os.getenv("REDMINE_USER")
    password = args.basic_password or os.getenv("REDMINE_PASSWORD")
    if user and password:
        encoded = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {encoded}"
        return headers

    raise ValueError(
        "Authentication required. Provide --api-key, --cred-file, or --basic-user/--basic-password (or REDMINE_API_KEY / REDMINE_USER / REDMINE_PASSWORD)."
    )


def build_body(args):
    body_sources = sum(bool(source) for source in (args.data, args.data_file, args.binary_file))
    if body_sources > 1:
        raise ValueError("Use only one body source: --data, --data-file, or --binary-file.")

    if args.binary_file:
        with open(args.binary_file, "rb") as fh:
            return fh.read()

    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as fh:
            raw = fh.read()
    elif args.data:
        raw = args.data
    else:
        return None

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}") from exc
    return json.dumps(parsed).encode("utf-8")


def make_url(base_url, endpoint, query):
    base = base_url.rstrip("/")
    path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    if query:
        encoded = urllib.parse.urlencode(query)
        return f"{base}{path}?{encoded}"
    return f"{base}{path}"


def print_response(status, body):
    print(f"HTTP {status}")
    if not body:
        return
    text = body.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text)
        print(json.dumps(parsed, indent=2, sort_keys=True))
    except json.JSONDecodeError:
        print(text)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Redmine REST API helper")
    parser.add_argument(
        "method",
        choices=["GET", "POST", "PUT", "DELETE"],
        help="HTTP method",
    )
    parser.add_argument("endpoint", help="API endpoint path, e.g. /issues.json")
    parser.add_argument(
        "--base-url",
        default=os.getenv("REDMINE_BASE_URL"),
        help="Redmine base URL (required; may also be provided via REDMINE_BASE_URL)",
    )
    parser.add_argument("--api-key", help="Redmine API key (or use REDMINE_API_KEY)")
    parser.add_argument(
        "--user-agent",
        help="User-Agent header (or use REDMINE_USER_AGENT). Default: curl/8.7.1",
    )
    parser.add_argument("--cred-file", help="File containing username:password")
    parser.add_argument("--basic-user", help="Basic auth username (or REDMINE_USER)")
    parser.add_argument("--basic-password", help="Basic auth password (or REDMINE_PASSWORD)")
    parser.add_argument("--query", action="append", default=[], help="Query parameter key=value")
    parser.add_argument("--data", help="Inline JSON body for POST/PUT")
    parser.add_argument("--data-file", help="Path to JSON body file for POST/PUT")
    parser.add_argument(
        "--binary-file",
        help="Path to raw request body bytes (for example, uploads)",
    )
    parser.add_argument(
        "--content-type",
        default="application/octet-stream",
        help="Content-Type when using --binary-file (default: application/octet-stream)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout in seconds (default: 30)",
    )
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    args = parser.parse_args()

    try:
        if not args.base_url:
            raise ValueError("Base URL is required. Pass --base-url or set REDMINE_BASE_URL.")
        if args.timeout <= 0:
            raise ValueError("--timeout must be greater than 0.")
        query = parse_query(args.query)
        body = build_body(args)
        headers = build_headers(args)
    except (OSError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    if body is not None:
        if args.binary_file:
            headers["Content-Type"] = args.content_type
        else:
            headers["Content-Type"] = "application/json"

    url = make_url(args.base_url, args.endpoint, query)
    request = urllib.request.Request(url=url, data=body, method=args.method, headers=headers)

    ssl_context = None
    if args.insecure:
        ssl_context = ssl._create_unverified_context()  # noqa: SLF001

    try:
        with urllib.request.urlopen(request, context=ssl_context, timeout=args.timeout) as resp:
            print_response(resp.status, resp.read())
            return 0
    except urllib.error.HTTPError as exc:
        err_body = exc.read()
        print_response(exc.code, err_body)
        return 1
    except urllib.error.URLError as exc:
        print(f"[ERROR] Request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
