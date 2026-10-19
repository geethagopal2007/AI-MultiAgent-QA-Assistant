
import unittest

from api_test_assistant import (
    validate_api_response,
    validate_json_fields,
    validate_error_status,
    generate_api_test_scenarios,
)


class TestValidateApiResponse(unittest.TestCase):

    def test_expected_status_passes(self):
        self.assertTrue(validate_api_response(200))

    def test_unexpected_status_fails(self):
        self.assertFalse(validate_api_response(404))


class TestValidateJsonFields(unittest.TestCase):

    def test_all_required_fields_present(self):
        data = {"id": 1, "name": "Geetha"}
        self.assertTrue(validate_json_fields(data, ["id", "name"]))

    def test_missing_required_field_fails(self):
        data = {"id": 1}
        self.assertFalse(validate_json_fields(data, ["id", "name"]))

    def test_non_dictionary_response_fails(self):
        self.assertFalse(validate_json_fields([], ["id"]))

    def test_expected_values_match(self):
        data = {"status": "success", "id": 10}
        self.assertTrue(
            validate_json_fields(
                data,
                ["status", "id"],
                {"status": "success", "id": 10},
            )
        )

    def test_expected_values_do_not_match(self):
        data = {"status": "failed", "id": 10}
        self.assertFalse(
            validate_json_fields(
                data,
                ["status"],
                {"status": "success"},
            )
        )


class TestValidateErrorStatus(unittest.TestCase):

    def test_common_error_status_passes(self):
        for status in (400, 401, 403, 404, 500):
            with self.subTest(status=status):
                self.assertTrue(validate_error_status(status))

    def test_success_status_fails(self):
        self.assertFalse(validate_error_status(200))

    def test_custom_error_status_list(self):
        self.assertTrue(validate_error_status(422, (422, 500)))
        self.assertFalse(validate_error_status(404, (422, 500)))


class TestGenerateApiTestScenarios(unittest.TestCase):

    def test_valid_endpoint_returns_three_scenarios(self):
        scenarios = generate_api_test_scenarios("/api/users")
        self.assertEqual(len(scenarios), 3)

    def test_empty_endpoint_returns_empty_list(self):
        self.assertEqual(generate_api_test_scenarios(""), [])

    def test_scenarios_have_required_fields(self):
        scenarios = generate_api_test_scenarios("/api/users")

        for scenario in scenarios:
            with self.subTest(test_id=scenario["test_id"]):
                self.assertEqual(
                    set(scenario.keys()),
                    {"test_id", "scenario", "expected_result"},
                )


if __name__ == "__main__":
    unittest.main()
