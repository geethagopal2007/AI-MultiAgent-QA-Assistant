
"""
API Test Assistant - Version 4.1

Rule-based API validation helpers.
No API key or third-party packages required.
"""


def validate_api_response(status_code, expected_status=200):
    """Check whether the HTTP status matches the expected status."""
    return status_code == expected_status


def validate_json_fields(response_data, required_fields, expected_values=None):
    """
    Validate required JSON fields and, optionally, their expected values.

    expected_values example:
        {"status": "success", "id": 10}
    """
    if not isinstance(response_data, dict):
        return False

    if not all(field in response_data for field in required_fields):
        return False

    if expected_values is not None:
        if not isinstance(expected_values, dict):
            return False

        for field, expected_value in expected_values.items():
            if field not in response_data:
                return False

            if response_data[field] != expected_value:
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
                "Invalid requests return appropriate error statuses, "
                "such as 400, 401, 403, 404, or 500, where applicable."
            ),
        },
    ]
