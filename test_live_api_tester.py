
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from live_api_tester import (
    run_live_api_test,
    export_live_api_html,
    export_live_api_csv,
    export_live_api_json,
)


class TestLiveApiTester(unittest.TestCase):

    @patch("live_api_tester.urlopen")
    def test_successful_api_response(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = response

        result = run_live_api_test(
            "https://example.com/api/users/1",
            expected_status=200,
            required_fields=["id", "name", "email"],
        )

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["json_data"]["id"], 1)

    @patch("live_api_tester.urlopen")
    def test_wrong_status_fails(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"id": 1}'
        mock_urlopen.return_value.__enter__.return_value = response

        result = run_live_api_test(
            "https://example.com/api/users/1",
            expected_status=201,
        )

        self.assertEqual(result["status"], "FAIL")

    @patch("live_api_tester.urlopen")
    def test_missing_required_field_fails(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"id": 1}'
        mock_urlopen.return_value.__enter__.return_value = response

        result = run_live_api_test(
            "https://example.com/api/users/1",
            required_fields=["id", "email"],
        )

        self.assertEqual(result["status"], "FAIL")

    @patch("live_api_tester.urlopen")
    def test_network_error_is_reported(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Network unavailable")

        result = run_live_api_test(
            "https://example.com/api/users/1"
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Request failed", result["message"])

    def test_invalid_url_raises_error(self):
        with self.assertRaises(ValueError):
            run_live_api_test("not-a-valid-url")

    def test_invalid_expected_status_raises_error(self):
        with self.assertRaises(ValueError):
            run_live_api_test(
                "https://example.com/api",
                expected_status=True,
            )

    def test_invalid_timeout_raises_error(self):
        with self.assertRaises(ValueError):
            run_live_api_test(
                "https://example.com/api",
                timeout=0,
            )


class TestLiveApiReportExports(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.result = {
            "test_id": "LIVE_API_01",
            "status": "PASS",
            "message": "API response validation passed.",
            "url": "https://example.com/api/users/1",
            "status_code": 200,
            "response_time_ms": 125.5,
            "json_data": {
                "id": 1,
                "name": "Test User",
            },
        }

    def test_html_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.html"

        returned_path = export_live_api_html(
            self.result, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        content = output.read_text(encoding="utf-8")
        self.assertIn("Live API Test Report", content)
        self.assertIn("LIVE_API_01", content)
        self.assertIn("PASS", content)
        self.assertIn("200", content)
        self.assertIn("Test User", content)

    def test_html_report_escapes_untrusted_content(self):
        result = dict(self.result)
        result["message"] = "<script>alert('x')</script>"

        output = Path(self.temp_dir.name) / "safe.html"
        export_live_api_html(result, str(output))

        content = output.read_text(encoding="utf-8")

        self.assertNotIn("<script>alert('x')</script>", content)
        self.assertIn("&lt;script&gt;", content)

    def test_csv_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.csv"

        returned_path = export_live_api_csv(
            self.result, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        with output.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["test_id"], "LIVE_API_01")
        self.assertEqual(rows[0]["status"], "PASS")
        self.assertEqual(rows[0]["status_code"], "200")

        response_data = json.loads(rows[0]["json_data"])
        self.assertEqual(response_data["name"], "Test User")

    def test_json_report_is_created(self):
        output = Path(self.temp_dir.name) / "report.json"

        returned_path = export_live_api_json(
            self.result, str(output)
        )

        self.assertTrue(Path(returned_path).exists())

        with output.open(encoding="utf-8") as file:
            report = json.load(file)

        self.assertEqual(report["test_id"], "LIVE_API_01")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["status_code"], 200)
        self.assertEqual(report["json_data"]["id"], 1)

    def test_failed_result_can_be_exported(self):
        result = dict(self.result)
        result["status"] = "FAIL"
        result["message"] = "Expected status did not match."

        output = Path(self.temp_dir.name) / "failed.json"
        export_live_api_json(result, str(output))

        with output.open(encoding="utf-8") as file:
            report = json.load(file)

        self.assertEqual(report["status"], "FAIL")
        self.assertIn("did not match", report["message"])

    def test_empty_json_response_can_be_exported(self):
        result = dict(self.result)
        result["json_data"] = None

        output = Path(self.temp_dir.name) / "empty.json"
        export_live_api_json(result, str(output))

        with output.open(encoding="utf-8") as file:
            report = json.load(file)

        self.assertIsNone(report["json_data"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
