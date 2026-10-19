
"""
AI Multi-Agent QA Assistant
Version 3 - Rule-based structured test generation

This version does not require an API key or external AI service.
"""


def generate_test_cases(requirement):
    """Generate the five legacy test-case descriptions."""
    if not isinstance(requirement, str) or not requirement.strip():
        return []

    requirement = requirement.strip()

    return [
        f"TC01 - Verify the main flow: {requirement}",
        f"TC02 - Verify invalid input handling for: {requirement}",
        f"TC03 - Verify required-field validation for: {requirement}",
        f"TC04 - Verify boundary conditions for: {requirement}",
        f"TC05 - Verify error handling for: {requirement}",
    ]


def generate_structured_test_cases(requirement):
    """Generate test cases in a structured format."""
    if not isinstance(requirement, str) or not requirement.strip():
        return []

    requirement = requirement.strip()

    scenarios = [
        (
            "Verify the main flow",
            "The requirement is processed successfully with valid input.",
        ),
        (
            "Verify invalid input handling",
            "Invalid input is rejected and a clear validation message is shown.",
        ),
        (
            "Verify required-field validation",
            "Missing required fields are identified and submission is prevented.",
        ),
        (
            "Verify boundary conditions",
            "Values at and beyond the permitted boundaries are handled correctly.",
        ),
        (
            "Verify error handling",
            "Errors are handled gracefully without exposing sensitive information.",
        ),
    ]

    return [
        {
            "test_id": f"TC{index:02d}",
            "scenario": scenario,
            "expected_result": expected_result,
        }
        for index, (scenario, expected_result) in enumerate(scenarios, start=1)
    ]


def main():
    """Run the assistant from the command line."""
    print("AI Multi-Agent QA Assistant - Version 3")
    requirement = input("Enter the software requirement: ").strip()

    if not requirement:
        print("Error: Requirement cannot be empty.")
        return

    print("\nGenerated structured test cases:\n")

    for test_case in generate_structured_test_cases(requirement):
        print(f"Test ID: {test_case['test_id']}")
        print(f"Scenario: {test_case['scenario']}")
        print(f"Expected Result: {test_case['expected_result']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
