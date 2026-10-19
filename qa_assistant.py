
"""
AI Multi-Agent QA Assistant
Version 2: Rule-based QA prototype
"""


def generate_test_cases(requirement):
    """Generate basic QA scenarios from a software requirement."""

    if not isinstance(requirement, str) or not requirement.strip():
        return ["ERROR: Please enter a requirement."]

    requirement = requirement.strip()

    return [
        f"TC01 - Verify the main flow: {requirement}",
        f"TC02 - Verify invalid input for: {requirement}",
        f"TC03 - Verify missing required fields for: {requirement}",
        f"TC04 - Verify boundary conditions for: {requirement}",
        f"TC05 - Verify error handling for: {requirement}",
    ]


def generate_structured_test_cases(requirement):
    """Generate test cases with steps and expected results."""

    basic_cases = generate_test_cases(requirement)

    if basic_cases[0].startswith("ERROR:"):
        return []

    expected_results = [
        "The main workflow completes successfully.",
        "Invalid input is rejected with a clear validation message.",
        "Missing required fields are identified.",
        "Boundary values are handled correctly.",
        "Errors are handled gracefully without unexpected failures.",
    ]

    structured_cases = []

    for index, case in enumerate(basic_cases):
        structured_cases.append({
            "test_id": f"TC{index + 1:03}",
            "scenario": case,
            "expected_result": expected_results[index],
        })

    return structured_cases


def main():
    print("=" * 45)
    print(" QA Assistant - Version 2")
    print(" Rule-based prototype")
    print("=" * 45)

    requirement = input("\nEnter a software requirement: ")

    test_cases = generate_structured_test_cases(requirement)

    if not test_cases:
        print("ERROR: Please enter a valid requirement.")
        return

    print(f"\nGenerated {len(test_cases)} test cases:\n")

    for case in test_cases:
        print(f"ID: {case['test_id']}")
        print(f"Scenario: {case['scenario']}")
        print(f"Expected: {case['expected_result']}")
        print("-" * 45)


if __name__ == "__main__":
    main()
