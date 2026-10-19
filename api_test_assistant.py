
"""
API Test Assistant - Version 5.0

Rule-based API validation helpers and report generation.
Uses only the Python standard library.
"""

import csv
import html
import json
from pathlib import Path


def validate_api_response(status_code, expected_status=200):
    """Check whether the HTTP status matches the expected status."""
    return (
        isinstance(status_code, int)
        and not isinstance(status_code, bool)
        and status_code == expected_status
    )


def _get_nested_value(response_data, field_path):
    """Retrieve a nested value using a dot-separated path."""
    if not isinstance(response_data, dict):
        return False, None

    if not isinstance(field_path, str) or not field_path.strip():
        return False, None

    value = response_data

    for key in field_path.split("."):
        if not isinstance(value, dict) or key not in value:
            return False, None
        value = value[key]

    return True, value


def validate_json_fields(response_data, required_fields, expected_values=None):
    """Validate required JSON fields and optional expected values."""
    if not isinstance(response_data, dict):
        return False

    if not isinstance(required_fields, (list, tuple)):
        return False

    for field in required_fields:
        found, _ = _get_nested_value(response_data, field)
        if not found:
            return False

    if expected_values is not None:
        if not isinstance(expected_values, dict):
            return False

        for field, expected_value in expected_values.items():
            found, actual_value = _get_nested_value(response_data, field)
            if not found or actual_value != expected_value:
                return False

    return True


def validate_json_field_types(response_data, expected_types):
    """Validate JSON field types, including nested fields."""
    if not isinstance(response_data, dict):
        return False

    if not isinstance(expected_types, dict):
        return False

    for field_path, expected_type in expected_types.items():
        if not isinstance(expected_type, type):
            return False

        found, value = _get_nested_value(response_data, field_path)
        if not found:
            return False

        if expected_type is int:
            if type(value) is not int:
                return False
        elif expected_type is bool:
            if type(value) is not bool:
                return False
        elif not isinstance(value, expected_type):
            return False

    return True


def validate_error_status(status_code, expected_statuses=None):
    """Check whether a response uses an expected HTTP error status."""
    if expected_statuses is None:
        expected_statuses = (400, 401, 403, 404, 500)

    if (
        not isinstance(status_code, int)
        or isinstance(status_code, bool)
        or not isinstance(expected_statuses, (list, tuple, set))
    ):
        return False

    return status_code in expected_statuses


def generate_api_test_scenarios(endpoint_name):
    """Generate basic API test scenarios."""
    if not isinstance(endpoint_name, str) or not endpoint_name.strip():
        return []

    endpoint_name = endpoint_name.strip()

    return [
        {
            "test_id": "API01",
            "scenario": f"Verify successful response from {endpoint_name}",
            "expected_result": "HTTP status matches the expected success status.",
        },
        {
            "test_id": "API02",
            "scenario": f"Verify required fields and values in {endpoint_name}",
            "expected_result": "Required fields exist and expected values match.",
        },
        {
            "test_id": "API03",
            "scenario": f"Verify error responses from {endpoint_name}",
            "expected_result": (
                "Invalid requests return appropriate HTTP error statuses."
            ),
        },
    ]


def generate_test_report(test_results):
    """
    Summarize test results.

    Each result must contain test_id and status (PASS or FAIL).
    An optional message can describe the outcome.
    """
    if not isinstance(test_results, list):
        raise TypeError("test_results must be a list")

    normalized_results = []

    for result in test_results:
        if not isinstance(result, dict):
            raise TypeError("Each test result must be a dictionary")

        test_id = result.get("test_id")
        status = result.get("status")
        message = result.get("message", "")

        if not isinstance(test_id, str) or not test_id.strip():
            raise ValueError("Each result must have a valid test_id")

        if not isinstance(status, str) or status not in ("PASS", "FAIL"):
            raise ValueError("status must be PASS or FAIL")

        if not isinstance(message, str):
            raise TypeError("message must be a string")

        normalized_results.append({
            "test_id": test_id.strip(),
            "status": status,
            "message": message,
        })

    passed = sum(r["status"] == "PASS" for r in normalized_results)
    failed = len(normalized_results) - passed

    return {
        "total": len(normalized_results),
        "passed": passed,
        "failed": failed,
        "results": normalized_results,
    }


def generate_html_report(test_results, output_file="api_test_report.html"):
    """Create a standalone HTML report and return its file path."""
    report = generate_test_report(test_results)

    rows = []
    for result in report["results"]:
        test_id = html.escape(result["test_id"])
        status = result["status"]
        message = html.escape(result["message"])
        rows.append(
            "<tr>"
            f"<td>{test_id}</td>"
            f'<td class="{status.lower()}">{status}</td>'
            f"<td>{message}</td>"
            "</tr>"
        )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; color: #222; }}
h1 {{ color: #17365d; }}
.summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0; }}
.card {{ padding: 16px; border-radius: 8px; background: #f1f5f9; }}
.pass {{ color: #16803c; font-weight: bold; }}
.fail {{ color: #c62828; font-weight: bold; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background: #17365d; color: white; }}
tr:nth-child(even) {{ background: #f8fafc; }}
</style>
</head>
<body>
<h1>API Test Report</h1>
<p>Generated by API Test Assistant</p>
<div class="summary">
<div class="card">Total tests: <strong>{report["total"]}</strong></div>
<div class="card">Passed: <strong class="pass">{report["passed"]}</strong></div>
<div class="card">Failed: <strong class="fail">{report["failed"]}</strong></div>
</div>
<table>
<thead><tr><th>Test ID</th><th>Status</th><th>Message</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
</body>
</html>
"""

    path = Path(output_file)
    path.write_text(page, encoding="utf-8")
    return str(path)


def export_test_report_csv(test_results, output_file="api_test_report.csv"):
    """Export individual test results to CSV and return its file path."""
    report = generate_test_report(test_results)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file, fieldnames=["test_id", "status", "message"]
        )
        writer.writeheader()
        writer.writerows(report["results"])

    return str(output_file)


def export_test_report_json(test_results, output_file="api_test_report.json"):
    """Export the report summary and results to JSON."""
    report = generate_test_report(test_results)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    return str(output_file)


if __name__ == "__main__":
    sample_results = [
        {
            "test_id": "API01",
            "status": "PASS",
            "message": "HTTP 200 received.",
        },
        {
            "test_id": "API02",
            "status": "FAIL",
            "message": "Required field 'email' is missing.",
        },
    ]

    report = generate_test_report(sample_results)
    print(json.dumps(report, indent=2))

    print("HTML report:", generate_html_report(sample_results))
    print("CSV report:", export_test_report_csv(sample_results))
    print("JSON report:", export_test_report_json(sample_results))
