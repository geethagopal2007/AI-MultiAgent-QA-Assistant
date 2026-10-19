
"""
API Test Assistant - Version 4.2

Rule-based API validation helpers.
No API key or third-party packages required.
"""


def validate_api_response(status_code, expected_status=200):
    """Check whether the HTTP status matches the expected status."""
    return status_code == expected_status


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
    """
    Validate required JSON fields and optional expected values.
    Supports nested paths such as 'user.id'.
    """
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
    """
    Validate JSON field types.

    Example:
        {"user.id": int, "user.name": str, "user.active": bool}
    """
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

        # Avoid accepting True/False as integers.
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

    return (
        isinstance(status_code, int)
        and not isinstance(status_code, bool)
        and status_code in expected_statuses
    )


def generate_api_test_scenarios(endpoint_name):
    """Generate basic success, response-validation, and error scenarios."""
    if not isinstance(endpoint_name, str) or not endpoint_name.strip():
        return []

    endpoint_name = endpoint_name.strip()

    return [
        {
            "test_id": "API01",
            "scenario": f"Verify successful response from {endpoint_name}",
            "expected_result": (
                "HTTP status matches the expected success status."
            ),
        },
        {
            "test_id": "API02",
            "scenario": f"Verify required fields and values in {endpoint_name}",
            "expected_result": (
                "Required fields exist and expected values match."
            ),
        },
        {
            "test_id": "API03",
            "scenario": f"Verify error responses from {endpoint_name}",
            "expected_result": (
                "Invalid requests return appropriate error statuses, "
                "such as 400, 401, 403, 404, or 500, where applicable."
            ),
        },
    ]
    
def generate_test_report(test_results):
    """
    Generate a summary report from API test results.

    Each result should contain:
        test_id, status, and optionally message.
    """
    if not isinstance(test_results, list):
        raise TypeError("test_results must be a list")

    normalized_results = []

    for result in test_results:
        if not isinstance(result, dict):
            raise TypeError("Each test result must be a dictionary")

        test_id = result.get("test_id")
        status = result.get("status")

        if not isinstance(test_id, str) or not test_id.strip():
            raise ValueError("Each result must have a valid test_id")

        if status not in ("PASS", "FAIL"):
            raise ValueError("status must be PASS or FAIL")

        message = result.get("message", "")
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        normalized_results.append({
            "test_id": test_id,
            "status": status,
            "message": message,
        })

    passed = sum(
        1 for result in normalized_results
        if result["status"] == "PASS"
    )
    failed = len(normalized_results) - passed

    return {
        "total": len(normalized_results),
        "passed": passed,
        "failed": failed,
        "results": normalized_results,
    }

