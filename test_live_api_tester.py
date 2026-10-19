
import json
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from live_api_tester import run_live_api_test


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


if __name__ == "__main__":
    unittest.main()
