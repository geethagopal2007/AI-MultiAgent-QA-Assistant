
import unittest

from qa_assistant import (
    generate_test_cases,
    generate_structured_test_cases,
)


class TestGenerateTestCases(unittest.TestCase):

    def test_empty_requirement_returns_empty_list(self):
        self.assertEqual(generate_test_cases(""), [])

    def test_whitespace_requirement_returns_empty_list(self):
        self.assertEqual(generate_test_cases("   "), [])

    def test_valid_requirement_returns_five_cases(self):
        cases = generate_test_cases("User login")
        self.assertEqual(len(cases), 5)

    def test_legacy_cases_are_strings(self):
        cases = generate_test_cases("User login")
        self.assertTrue(all(isinstance(case, str) for case in cases))


class TestGenerateStructuredTestCases(unittest.TestCase):

    def test_empty_requirement_returns_empty_list(self):
        self.assertEqual(generate_structured_test_cases(""), [])

    def test_whitespace_requirement_returns_empty_list(self):
        self.assertEqual(generate_structured_test_cases("   "), [])

    def test_valid_requirement_returns_five_cases(self):
        cases = generate_structured_test_cases("User login")
        self.assertEqual(len(cases), 5)

    def test_structured_cases_have_required_fields(self):
        cases = generate_structured_test_cases("User login")

        self.assertEqual(
            set(cases[0].keys()),
            {"test_id", "scenario", "expected_result"},
        )
        self.assertEqual(cases[0]["test_id"], "TC01")
        self.assertTrue(cases[0]["scenario"])
        self.assertTrue(cases[0]["expected_result"])


if __name__ == "__main__":
    unittest.main()
