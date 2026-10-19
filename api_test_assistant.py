
"""
API Test Assistant - Version 4
Basic API response validation without external packages.
"""

def validate_api_response(status_code, expected_status=200):
    """Check whether the HTTP status matches the expected status."""
    return status_code == expected_status


def validate_json_fields(response_data, required_fields):
    """Check that required fields exist in a JSON-like dictionary."""
    if not isinstance(response_data, dict):
        return False

    return all(field in response_data for field in required_fields)


def generate_api_test_scenarios(endpoint_name):
    """Generate basic API testing scenarios."""
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
            "scenario": f"Verify required fields in {endpoint_name} response",
            "expected_result": "All required response fields are present.",
        },
        {
            "test_id": "API03",
            "scenario": f"Verify invalid request handling for {endpoint_name}",
            "expected_result": "Invalid requests are handled with an appropriate error response.",
        },
    ]

