
import unittest

from qa_assistant import (
    generate_test_cases,
    generate_structured_test_cases,
)


class TestGenerateTestCases(unittest.TestCase):

    def test_generates_five_scenarios(self):
        cases = generate_test_cases("User login")
        self.assertEqual(len(cases), 5)

    def test_includes_main_flow(self):
        cases = generate_test_cases("User login")
        self.assertIn(
            "TC01 - Verify the main flow: User login",
            cases,
        )

    def test_includes_invalid_input(self):
        cases = generate_test_cases("User registration")
        self.assertTrue(
            any("invalid input" in case for case in cases)
        )

    def test_empty_requirement(self):
        cases = generate_test_cases("   ")
        self.assertEqual(
            cases,
            ["ERROR: Please enter a requirement."],
        )


class TestStructuredTestCases(unittest.TestCase):

    def test_generates_five_structured_cases(self):
        cases = generate_structured_test_cases("User login")
        self.assertEqual(len(cases), 5)

    def test_has_required_fields(self):
        cases = generate_structured_test_cases("User login")

        for case in cases:
            self.assertIn("test_id", case)
            self.assertIn("scenario", case)
            self.assertIn("expected_result", case)

    def test_test_ids_are_unique(self):
        cases = generate_structured_test_cases("User login")
        ids = [case["test_id"] for case in cases]

        self.assertEqual(len(ids), len(set(ids)))

    def test_empty_requirement_returns_no_structured_cases(self):
        cases = generate_structured_test_cases("   ")
        self.assertEqual(cases, [])

if __name__ == "__main__":
    unittest.main()
