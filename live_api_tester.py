
"""
Live API Tester v4
Scenario-aware API test execution and reporting.
"""

import csv
import html
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


ALLOWED_METHODS = {
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"
}


def validate_url(url):
    if not isinstance(url, str) or not url.strip():
        raise ValueError("A URL is required.")

    parsed = urlparse(url.strip())

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Enter a valid HTTP/HTTPS URL.")

    return url.strip()


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
    """Execute one request and validate its HTTP response."""

    url = validate_url(url)
    method = str(method).upper().strip()

    if method not in ALLOWED_METHODS:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if not isinstance(expected_status, int) or not 100 <= expected_status <= 599:
        raise ValueError("Expected status must be between 100 and 599.")

    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero.")

    required_fields = required_fields or []

    request_headers = {
        "Accept": "application/json",
        "User-Agent": "MultiAgent-QA-Assistant/4.0",
    }

    if headers:
        request_headers.update(headers)

    data = None

    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, str):
            data = body.encode("utf-8")
        elif isinstance(body, bytes):
            data = body
        else:
            raise ValueError("body must be a dict, list, string or bytes.")

    request = Request(
        url=url,
        data=data,
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
        except HTTPError as exc:
            # HTTP 4xx/5xx are real responses, not transport errors.
            status_code = exc.code
            response_body = exc.read()
            response_headers = dict(exc.headers.items())
    except (URLError, TimeoutError, OSError) as exc:
        error_message = f"{type(exc).__name__}: {exc}"

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
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
            error_message is None and elapsed_ms <= max_response_time_ms
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
    """Backward-compatible GET test for the dashboard."""

    result = execute_api_request(
        url=url,
        method="GET",
        expected_status=int(expected_status),
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
    Execute tests according to scenario.

    Authentication checks are BLOCKED unless a protected endpoint
    and an appropriate authentication test configuration are supplied.
    """

    if not isinstance(test_case, dict):
        raise ValueError("test_case must be a dictionary.")

    scenario = str(test_case.get("scenario", "")).lower()
    test_id = str(test_case.get("test_case_id", "API_TEST"))

    result = None

    # 1. Invalid endpoint: expect a genuine 404 response.
    if "invalid endpoint" in scenario:
        parsed = urlparse(validate_url(url))
        invalid_path = parsed.path.rstrip("/") + "/__qa_invalid_endpoint__"
        invalid_url = urlunparse(parsed._replace(path=invalid_path))

        result = execute_api_request(
            url=invalid_url,
            method="GET",
            expected_status=404,
            required_fields=[],
            timeout=timeout,
        )

        result["message"] = (
            "Invalid endpoint correctly returned HTTP 404."
            if result["status"] == "PASS"
            else (
                "Expected HTTP 404 for the invalid endpoint; "
                f"received {result.get('status_code')}."
            )
        )

    # 2. Unsupported method: TRACE must be rejected by the server.
    elif "unsupported http method" in scenario:
        result = execute_api_request(
            url=url,
            method="TRACE",
            expected_status=405,
            required_fields=[],
            timeout=timeout,
        )

        code = result.get("status_code")
        passed = code in (405, 501) and result.get("message") != "Request failed"

        result["status"] = "PASS" if passed else "FAIL"
        result["expected_status"] = "405 or 501"
        result["checks"]["unsupported_method_rejected"] = passed
        result["message"] = (
            "Server rejected TRACE as expected."
            if passed
            else f"TRACE was not rejected as expected; HTTP status: {code}."
        )

    # 3. Authentication cannot be assumed for a public endpoint.
    elif "authentication" in scenario:
        result = {
            "status": "BLOCKED",
            "message": (
                "Configure a protected endpoint and authentication "
                "credentials to run this test."
            ),
            "url": url,
            "method": method,
            "status_code": None,
            "response_time_ms": None,
            "checks": {"authentication_test_configured": False},
        }

    # 4. Response-time scenario.
    elif "response time" in scenario:
        result = execute_api_request(
            url=url,
            method=method,
            expected_status=int(expected_status),
            required_fields=[],
            timeout=timeout,
            max_response_time_ms=timeout * 1000,
        )

    # 5. Required fields / response structure / field values.
    elif any(
        keyword in scenario
        for keyword in (
            "required response fields",
            "response structure",
            "response field values",
        )
    ):
        result = execute_api_request(
            url=url,
            method=method,
            expected_status=int(expected_status),
            required_fields=required_fields,
            timeout=timeout,
        )

        if result.get("status") == "PASS":
            data = result.get("json_data")

            if "response structure" in scenario:
                valid_structure = isinstance(data, (dict, list))
                result["checks"]["valid_json_structure"] = valid_structure
                result["status"] = "PASS" if valid_structure else "FAIL"

            if "response field values" in scenario:
                valid_values = (
                    isinstance(data, dict)
                    and all(
                        field in data and data[field] is not None
                        for field in (required_fields or [])
                    )
                )
                result["checks"]["field_values_non_null"] = valid_values
                result["status"] = "PASS" if valid_values else "FAIL"

    # 6. Default functional request.
    else:
        result = execute_api_request(
            url=url,
            method=method,
            expected_status=int(expected_status),
            required_fields=required_fields,
            timeout=timeout,
        )

    result["test_id"] = test_id
    result["scenario"] = test_case.get("scenario", "")
    result["test_type"] = test_case.get("test_type", "")
    result["steps"] = test_case.get("steps", "")
    result["expected_result"] = test_case.get("expected_result", "")

    return result


def build_html_report(results):
    rows = []

    for item in results:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('test_id', '')))}</td>"
            f"<td>{html.escape(str(item.get('scenario', '')))}</td>"
            f"<td>{html.escape(str(item.get('status', '')))}</td>"
            f"<td>{html.escape(str(item.get('status_code', '')))}</td>"
            f"<td>{html.escape(str(item.get('message', '')))}</td>"
            "</tr>"
        )

    passed = sum(item.get("status") == "PASS" for item in results)
    failed = sum(item.get("status") == "FAIL" for item in results)
    blocked = sum(item.get("status") == "BLOCKED" for item in results)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>API Test Execution Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #17365d; color: white; }}
</style>
</head>
<body>
<h1>API Test Execution Report</h1>
<p>Total: {len(results)} | PASS: {passed} | FAIL: {failed} | BLOCKED: {blocked}</p>
<table>
<thead><tr>
<th>Test ID</th><th>Scenario</th><th>Status</th>
<th>HTTP Status</th><th>Message</th>
</tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
</body>
</html>"""


def export_live_api_csv(result, output_file="live_api_report.csv"):
    fields = [
        "test_id", "status", "message", "url", "method",
        "status_code", "expected_status", "response_time_ms",
        "checks", "json_data",
    ]

    row = {field: result.get(field, "") for field in fields}
    row["checks"] = json.dumps(result.get("checks", {}), ensure_ascii=False)
    row["json_data"] = json.dumps(result.get("json_data"), ensure_ascii=False)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)

    return str(output_file)


def export_live_api_json(result, output_file="live_api_report.json"):
    Path(output_file).write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return str(output_file)


def export_live_api_html(result, output_file="live_api_report.html"):
    Path(output_file).write_text(
        build_html_report([result]),
        encoding="utf-8",
    )
    return str(output_file)


if __name__ == "__main__":
    result = run_live_api_test(
        "https://jsonplaceholder.typicode.com/users/1",
        expected_status=200,
        required_fields=["id", "name", "email"],
        timeout=10,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
