
"""
Live API Tester - Version 3.0

Features:
- GET, POST, PUT, PATCH and DELETE
- HTTP status validation
- Required JSON field validation
- Response-time validation
- Safe error handling
- Individual test case execution
- HTML, CSV and JSON report exports

Uses only the Python standard library.
"""

import csv
import html
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def validate_url(url):
    """Validate basic HTTP/HTTPS URL syntax."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    url = url.strip()
    parsed = urlparse(url)

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("A valid HTTP/HTTPS URL is required")

    return url


def execute_api_request(
    url,
    method="GET",
    expected_status=200,
    required_fields=None,
    timeout=10,
    headers=None,
    body=None,
    max_response_time_ms=None,
):
    """
    Execute one HTTP request and return structured validation results.

    body can be a Python dictionary/list or a JSON string.
    """

    url = validate_url(url)
    method = str(method).upper().strip()

    if method not in ALLOWED_METHODS:
        raise ValueError(
            f"Unsupported method. Use one of: {sorted(ALLOWED_METHODS)}"
        )

    if (
        not isinstance(expected_status, int)
        or isinstance(expected_status, bool)
        or not 100 <= expected_status <= 599
    ):
        raise ValueError("expected_status must be between 100 and 599")

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("timeout must be greater than zero")

    if max_response_time_ms is not None:
        if (
            not isinstance(max_response_time_ms, (int, float))
            or isinstance(max_response_time_ms, bool)
            or max_response_time_ms <= 0
        ):
            raise ValueError(
                "max_response_time_ms must be greater than zero"
            )

    if required_fields is None:
        required_fields = []

    if not isinstance(required_fields, (list, tuple)):
        raise ValueError("required_fields must be a list or tuple")

    for field in required_fields:
        if not isinstance(field, str) or not field.strip():
            raise ValueError("Required fields must be non-empty strings")

    request_headers = {
        "Accept": "application/json",
        "User-Agent": "MultiAgent-QA-Assistant/3.0",
    }

    if headers:
        if not isinstance(headers, dict):
            raise ValueError("headers must be a dictionary")
        request_headers.update(headers)

    request_data = None

    if body is not None:
        if isinstance(body, (dict, list)):
            request_data = json.dumps(body).encode("utf-8")
            request_headers.setdefault(
                "Content-Type", "application/json"
            )
        elif isinstance(body, str):
            request_data = body.encode("utf-8")
        elif isinstance(body, bytes):
            request_data = body
        else:
            raise ValueError(
                "body must be a dictionary, list, string, bytes or None"
            )

    request = Request(
        url=url,
        data=request_data,
        headers=request_headers,
        method=method,
    )

    start = time.perf_counter()
    status_code = None
    response_body = b""
    response_headers = {}
    error_message = None

    try:
        try:
            with urlopen(request, timeout=timeout) as response:
                status_code = response.status
                response_body = response.read()
                response_headers = dict(response.headers.items())

        except HTTPError as error:
            # HTTP errors such as 400 and 404 are valid HTTP responses.
            status_code = error.code
            response_body = error.read()
            response_headers = dict(error.headers.items())

    except (URLError, TimeoutError, OSError) as error:
        error_message = f"Request failed: {error}"

    elapsed_ms = round(
        (time.perf_counter() - start) * 1000, 2
    )

    response_text = response_body.decode("utf-8", errors="replace")

    try:
        response_json = json.loads(response_text)
    except (json.JSONDecodeError, ValueError):
        response_json = None

    checks = {
        "request_completed": error_message is None,
        "http_status": status_code == expected_status,
    }

    if required_fields:
        checks["required_fields"] = (
            isinstance(response_json, dict)
            and all(field in response_json for field in required_fields)
        )

    if max_response_time_ms is not None:
        checks["response_time"] = (
            error_message is None
            and elapsed_ms <= max_response_time_ms
        )

    passed = all(checks.values())

    return {
        "test_id": "API_TEST",
        "status": "PASS" if passed else "FAIL",
        "message": (
            "All validations passed."
            if passed
            else error_message or "One or more validations failed."
        ),
        "url": url,
        "method": method,
        "status_code": status_code,
        "expected_status": expected_status,
        "response_time_ms": elapsed_ms,
        "max_response_time_ms": max_response_time_ms,
        "checks": checks,
        "response_headers": response_headers,
        "json_data": response_json,
        "response_text": response_text[:10000],
    }


def run_live_api_test(
    url,
    expected_status=200,
    required_fields=None,
    timeout=10,
):
    """
    Backward-compatible function used by the existing dashboard.
    Continues to execute GET requests.
    """
    result = execute_api_request(
        url=url,
        method="GET",
        expected_status=expected_status,
        required_fields=required_fields,
        timeout=timeout,
    )

    result["test_id"] = "LIVE_API_01"
    return result


def run_api_test_case(
    test_case,
    url,
    method="GET",
    required_fields=None,
    timeout=10,
    expected_status=200,
):
    """
    Execute a generated test case against an API endpoint.

    The expected status can be overridden for negative tests.
    This function does not infer undocumented business rules.
    """
    if not isinstance(test_case, dict):
        raise ValueError("test_case must be a dictionary")

    result = execute_api_request(
        url=url,
        method=method,
        expected_status=expected_status,
        required_fields=required_fields,
        timeout=timeout,
    )

    result["test_id"] = str(
        test_case.get("test_case_id", "API_TEST")
    )
    result["scenario"] = str(test_case.get("scenario", ""))
    result["test_type"] = str(test_case.get("test_type", ""))
    result["steps"] = str(test_case.get("steps", ""))
    result["expected_result"] = str(
        test_case.get("expected_result", "")
    )

    return result


def export_live_api_html(
    result,
    output_file="live_api_report.html",
):
    """Export one API result as an HTML report."""

    def safe(value):
        return html.escape(str(value if value is not None else ""))

    status = result.get("status", "FAIL")
    status = status if status in ("PASS", "FAIL") else "FAIL"

    response_json = json.dumps(
        result.get("json_data"),
        indent=2,
        ensure_ascii=False,
    )

    checks_json = json.dumps(
        result.get("checks", {}),
        indent=2,
        ensure_ascii=False,
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
<p>Test ID: {safe(result.get("test_id"))}</p>
<p>Status: <span class="{status.lower()}">{status}</span></p>
<p>Message: {safe(result.get("message"))}</p>
<p>Method: {safe(result.get("method"))}</p>
<p>URL: {safe(result.get("url"))}</p>
<p>HTTP Status: {safe(result.get("status_code"))}</p>
<p>Response Time (ms): {safe(result.get("response_time_ms"))}</p>
<h2>Validation Checks</h2>
<pre>{safe(checks_json)}</pre>
<h2>JSON Response</h2>
<pre>{safe(response_json)}</pre>
</body>
</html>
"""

    path = Path(output_file)
    path.write_text(page, encoding="utf-8")
    return str(path)


def export_live_api_csv(
    result,
    output_file="live_api_report.csv",
):
    """Export one API result as CSV."""

    fields = [
        "test_id",
        "status",
        "message",
        "url",
        "method",
        "status_code",
        "expected_status",
        "response_time_ms",
        "checks",
        "json_data",
    ]

    row = {field: result.get(field, "") for field in fields}
    row["checks"] = json.dumps(
        result.get("checks", {}),
        ensure_ascii=False,
    )
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


def export_live_api_json(
    result,
    output_file="live_api_report.json",
):
    """Export one API result as JSON."""

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
