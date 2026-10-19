
import unittest

from qa_assistant import generate_test_cases


class TestGenerateTestCases(unittest.TestCase):

    def test_generates_five_scenarios(self):
        cases = generate_test_cases("User login")
        self.assertEqual(len(cases), 5)

    def test_includes_main_flow(self):
        cases = generate_test_cases("User login")
        self.assertIn("TC01 - Verify the main flow: User login", cases)

    def test_includes_invalid_input(self):
        cases = generate_test_cases("User registration")
        self.assertTrue(any("invalid input" in c for c in cases))

    def test_empty_requirement(self):
        cases = generate_test_cases("   ")
        self.assertEqual(
            cases,
            ["ERROR: Please enter a requirement."]
        )


if __name__ == "__main__":
    unittest.main()
