
"""
Live API Tester - Version 1.0

Sends real HTTP GET requests and validates API responses.
Uses only the Python standard library.
"""

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def run_live_api_test(
    url,
    expected_status=200,
    required_fields=None,
    timeout=10,
):
    """
    Send a real GET request and validate the response.

    Returns a dictionary containing status, HTTP status code,
    response time, message, and parsed JSON when available.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    parsed = urlparse(url.strip())

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

    if required_fields is not None and not isinstance(
        required_fields, (list, tuple)
    ):
        raise ValueError("required_fields must be a list or tuple")

    request = Request(
        url.strip(),
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

        checks = []

        checks.append(status_code == expected_status)

        if required_fields is not None:
            checks.append(isinstance(response_data, dict))

            if isinstance(response_data, dict):
                checks.append(
                    all(
                        isinstance(field, str)
                        and field in response_data
                        for field in required_fields
                    )
                )
            else:
                checks.append(False)

        passed = all(checks)

        return {
            "test_id": "LIVE_API_01",
            "status": "PASS" if passed else "FAIL",
            "message": (
                "API response validation passed."
                if passed
                else "API response validation failed."
            ),
            "url": url.strip(),
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "json_data": response_data,
        }

    except (URLError, TimeoutError, OSError, ValueError) as error:
        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        return {
            "test_id": "LIVE_API_01",
            "status": "FAIL",
            "message": f"Request failed: {error}",
            "url": url.strip(),
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "json_data": response_data,
        }


if __name__ == "__main__":
    result = run_live_api_test(
        "https://jsonplaceholder.typicode.com/users/1",
        expected_status=200,
        required_fields=["id", "name", "email"],
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
