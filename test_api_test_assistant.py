
import unittest
import csv
import json
import tempfile
from pathlib import Path

from api_test_assistant import (
    validate_api_response,
    validate_json_fields,
    validate_json_field_types,
    validate_error_status,
    generate_api_test_scenarios,
    generate_test_report,
    generate_html_report,
    export_test_report_csv,
    export_test_report_json,
)


class TestValidateApiResponse(unittest.TestCase):

    def test_expected_status_passes(self):
        self.assertTrue(validate_api_response(200))

    def test_unexpected_status_fails(self):
        self.assertFalse(validate_api_response(404))

    def test_boolean_status_fails(self):
        self.assertFalse(validate_api_response(True))


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

    def test_invalid_required_fields_type_fails(self):
        self.assertFalse(
            validate_json_fields({"id": 1}, "id")
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
            validate_json_field_types(
                self.data, {"user.id": str}
            )
        )

    def test_boolean_is_not_accepted_as_integer(self):
        self.assertFalse(
            validate_json_field_types(
                {"active": True}, {"active": int}
            )
        )

    def test_integer_is_not_accepted_as_boolean(self):
        self.assertFalse(
            validate_json_field_types(
                {"active": 1}, {"active": bool}
            )
        )

    def test_missing_field_fails(self):
        self.assertFalse(
            validate_json_field_types(
                self.data, {"user.email": str}
            )
        )

    def test_invalid_expected_type_fails(self):
        self.assertFalse(
            validate_json_field_types(
                self.data, {"user.id": "int"}
            )
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
        self.assertTrue(
            validate_error_status(422, (422, 500))
        )
        self.assertFalse(
            validate_error_status(404, (422, 500))
        )

    def test_boolean_status_fails(self):
        self.assertFalse(validate_error_status(True))


class TestGenerateApiTestScenarios(unittest.TestCase):

    def test_valid_endpoint_returns_three_scenarios(self):
        self.assertEqual(
            len(generate_api_test_scenarios("/api/users")), 3
        )

    def test_empty_endpoint_returns_empty_list(self):
        self.assertEqual(generate_api_test_scenarios(""), [])

    def test_whitespace_endpoint_returns_empty_list(self):
        self.assertEqual(generate_api_test_scenarios("   "), [])

    def test_scenarios_have_required_fields(self):
        scenarios = generate_api_test_scenarios("/api/users")

        for scenario in scenarios:
            with self.subTest(test_id=scenario["test_id"]):
                self.assertEqual(
                    set(scenario.keys()),
                    {"test_id", "scenario", "expected_result"},
                )


class TestGenerateTestReport(unittest.TestCase):

    def setUp(self):
        self.results = [
            {
                "test_id": "API01",
                "status": "PASS",
                "message": "HTTP 200 received",
            },
            {
                "test_id": "API02",
                "status": "FAIL",
                "message": "Email field missing",
            },
        ]

    def test_report_summary_counts(self):
        report = generate_test_report(self.results)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(len(report["results"]), 2)

    def test_empty_report(self):
        report = generate_test_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["results"], [])

    def test_non_list_input_raises_error(self):
        with self.assertRaises(TypeError):
            generate_test_report({})

    def test_non_dictionary_result_raises_error(self):
        with self.assertRaises(TypeError):
            generate_test_report(["invalid"])

    def test_missing_test_id_raises_error(self):
        with self.assertRaises(ValueError):
            generate_test_report(
                [{"status": "PASS", "message": "OK"}]
            )

    def test_invalid_status_raises_error(self):
        with self.assertRaises(ValueError):
            generate_test_report(
                [{"test_id": "API01", "status": "UNKNOWN"}]
            )

    def test_non_string_message_raises_error(self):
        with self.assertRaises(TypeError):
            generate_test_report(
                [
                    {
                        "test_id": "API01",
                        "status": "PASS",
                        "message": 123,
                    }
                ]
            )


class TestApiTestReports(unittest.TestCase):

    def setUp(self):
        self.results = [
            {
                "test_id": "API01",
                "status": "PASS",
                "message": "HTTP 200 received",
            },
            {
                "test_id": "API02",
                "status": "FAIL",
                "message": "Email field missing",
            },
        ]

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_html_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.html"

        returned_path = generate_html_report(
            self.results, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        content = output.read_text(encoding="utf-8")
        self.assertIn("API Test Report", content)
        self.assertIn("Total tests:", content)
        self.assertIn("Email field missing", content)
        self.assertIn("PASS", content)
        self.assertIn("FAIL", content)

    def test_html_report_escapes_untrusted_text(self):
        results = [
            {
                "test_id": "<script>alert(1)</script>",
                "status": "PASS",
                "message": "<b>untrusted</b>",
            }
        ]

        output = Path(self.temp_dir.name) / "safe.html"
        generate_html_report(results, str(output))
        content = output.read_text(encoding="utf-8")

        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("&lt;script&gt;", content)
        self.assertIn("&lt;b&gt;untrusted&lt;/b&gt;", content)

    def test_csv_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.csv"

        returned_path = export_test_report_csv(
            self.results, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        with output.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["status"], "PASS")
        self.assertEqual(rows[1]["status"], "FAIL")
        self.assertEqual(
            rows[1]["message"], "Email field missing"
        )

    def test_json_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.json"

        returned_path = export_test_report_json(
            self.results, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        with output.open(encoding="utf-8") as file:
            report = json.load(file)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(len(report["results"]), 2)

    def test_csv_and_json_handle_empty_results(self):
        csv_output = Path(self.temp_dir.name) / "empty.csv"
        json_output = Path(self.temp_dir.name) / "empty.json"

        export_test_report_csv([], str(csv_output))
        export_test_report_json([], str(json_output))

        with csv_output.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

        with json_output.open(encoding="utf-8") as file:
            report = json.load(file)

        self.assertEqual(rows, [])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["results"], [])


if __name__ == "__main__":
    unittest.main()
