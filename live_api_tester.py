
"""
Live API Tester - Version 2.0

Features:
- Send real HTTP GET requests
- Validate HTTP status and required JSON fields
- Measure response time
- Export HTML, CSV, and JSON reports
- Uses only the Python standard library
"""

import csv
import html
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def run_live_api_test(
    url,
    expected_status=200,
    required_fields=None,
    timeout=10,
):
    """Send a GET request and validate its response."""

    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("A valid HTTP or HTTPS URL is required")

    if (
        not isinstance(expected_status, int)
        or isinstance(expected_status, bool)
        or not 100 <= expected_status <= 599
    ):
        raise ValueError("expected_status must be an HTTP status code")

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("timeout must be greater than zero")

    if required_fields is not None:
        if not isinstance(required_fields, (list, tuple)):
            raise ValueError("required_fields must be a list or tuple")
        if any(
            not isinstance(field, str) or not field.strip()
            for field in required_fields
        ):
            raise ValueError("Each required field must be a non-empty string")

    request = Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    start = time.perf_counter()
    status_code = None
    response_data = None

    try:
        try:
            with urlopen(request, timeout=timeout) as response:
                status_code = response.status
                body = response.read()
        except HTTPError as error:
            status_code = error.code
            body = error.read()

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        try:
            response_data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            response_data = None

        checks = [status_code == expected_status]

        if required_fields is not None:
            fields_valid = isinstance(response_data, dict)

            if fields_valid:
                fields_valid = all(
                    field in response_data for field in required_fields
                )

            checks.append(fields_valid)

        passed = all(checks)

        return {
            "test_id": "LIVE_API_01",
            "status": "PASS" if passed else "FAIL",
            "message": (
                "API response validation passed."
                if passed
                else "API response validation failed."
            ),
            "url": url,
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "json_data": response_data,
        }

    except (URLError, TimeoutError, OSError) as error:
        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        return {
            "test_id": "LIVE_API_01",
            "status": "FAIL",
            "message": f"Request failed: {error}",
            "url": url,
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "json_data": response_data,
        }


def export_live_api_html(result, output_file="live_api_report.html"):
    """Export a live API result as an HTML report."""

    test_id = html.escape(str(result.get("test_id", "")))
    status = str(result.get("status", "FAIL"))
    safe_status = status if status in ("PASS", "FAIL") else "FAIL"
    message = html.escape(str(result.get("message", "")))
    url = html.escape(str(result.get("url", "")))
    status_code = html.escape(str(result.get("status_code", "")))
    response_time = html.escape(
        str(result.get("response_time_ms", ""))
    )
    json_data = html.escape(
        json.dumps(
            result.get("json_data"),
            indent=2,
            ensure_ascii=False,
        )
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Live API Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; color: #222; }}
.pass {{ color: green; font-weight: bold; }}
.fail {{ color: red; font-weight: bold; }}
pre {{ background: #f3f4f6; padding: 12px; overflow-wrap: anywhere; }}
</style>
</head>
<body>
<h1>Live API Test Report</h1>
<p>Test ID: {test_id}</p>
<p>Status: <span class="{safe_status.lower()}">{safe_status}</span></p>
<p>Message: {message}</p>
<p>URL: {url}</p>
<p>HTTP Status Code: {status_code}</p>
<p>Response Time (ms): {response_time}</p>
<h2>JSON Response</h2>
<pre>{json_data}</pre>
</body>
</html>
"""

    path = Path(output_file)
    path.write_text(page, encoding="utf-8")
    return str(path)


def export_live_api_csv(result, output_file="live_api_report.csv"):
    """Export a live API result as CSV."""

    fields = [
        "test_id",
        "status",
        "message",
        "url",
        "status_code",
        "response_time_ms",
        "json_data",
    ]

    row = {field: result.get(field, "") for field in fields}
    row["json_data"] = json.dumps(
        result.get("json_data"),
        ensure_ascii=False,
    )

    with open(
        output_file, "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)

    return str(output_file)


def export_live_api_json(result, output_file="live_api_report.json"):
    """Export a live API result as JSON."""

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    return str(output_file)


if __name__ == "__main__":
    result = run_live_api_test(
        "https://jsonplaceholder.typicode.com/users/1",
        expected_status=200,
        required_fields=["id", "name", "email"],
        timeout=10,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("HTML report:", export_live_api_html(result))
    print("CSV report:", export_live_api_csv(result))
    print("JSON report:", export_live_api_json(result))
