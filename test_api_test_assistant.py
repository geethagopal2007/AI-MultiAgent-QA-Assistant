
import unittest

from api_test_assistant import (
    validate_api_response,
    validate_json_fields,
    validate_json_field_types,
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
        self.assertTrue(
            validate_json_fields(
                {"id": 1, "name": "Geetha"},
                ["id", "name"],
            )
        )

    def test_missing_required_field_fails(self):
        self.assertFalse(
            validate_json_fields({"id": 1}, ["id", "name"])
        )

    def test_non_dictionary_response_fails(self):
        self.assertFalse(validate_json_fields([], ["id"]))

    def test_expected_values_match(self):
        self.assertTrue(
            validate_json_fields(
                {"status": "success", "id": 10},
                ["status", "id"],
                {"status": "success", "id": 10},
            )
        )

    def test_expected_values_do_not_match(self):
        self.assertFalse(
            validate_json_fields(
                {"status": "failed"},
                ["status"],
                {"status": "success"},
            )
        )

    def test_nested_fields_are_supported(self):
        data = {"user": {"id": 101, "name": "Geetha"}}
        self.assertTrue(
            validate_json_fields(data, ["user.id", "user.name"])
        )

    def test_missing_nested_field_fails(self):
        data = {"user": {"id": 101}}
        self.assertFalse(
            validate_json_fields(data, ["user.email"])
        )


class TestValidateJsonFieldTypes(unittest.TestCase):

    def setUp(self):
        self.data = {
            "user": {
                "id": 101,
                "name": "Geetha",
                "active": True,
                "score": 9.5,
            }
        }

    def test_nested_types_match(self):
        self.assertTrue(
            validate_json_field_types(
                self.data,
                {
                    "user.id": int,
                    "user.name": str,
                    "user.active": bool,
                    "user.score": float,
                },
            )
        )

    def test_wrong_type_fails(self):
        self.assertFalse(
            validate_json_field_types(self.data, {"user.id": str})
        )

    def test_boolean_is_not_accepted_as_integer(self):
        self.assertFalse(
            validate_json_field_types({"active": True}, {"active": int})
        )

    def test_missing_field_fails(self):
        self.assertFalse(
            validate_json_field_types(self.data, {"user.email": str})
        )

    def test_invalid_expected_type_fails(self):
        self.assertFalse(
            validate_json_field_types(self.data, {"user.id": "int"})
        )

    def test_non_dictionary_response_fails(self):
        self.assertFalse(
            validate_json_field_types([], {"id": int})
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
        self.assertEqual(
            len(generate_api_test_scenarios("/api/users")), 3
        )

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
