
def generate_test_cases(requirement):
    """Generate basic QA scenarios from a requirement."""
    requirement = requirement.strip()

    if not requirement:
        return ["ERROR: Please enter a requirement."]

    return [
        f"TC01 - Verify the main flow: {requirement}",
        f"TC02 - Verify invalid input for: {requirement}",
        f"TC03 - Verify missing required fields for: {requirement}",
        f"TC04 - Verify boundary conditions for: {requirement}",
        f"TC05 - Verify error handling for: {requirement}",
    ]


def main():
    print("AI Multi-Agent QA Assistant - Prototype")
    requirement = input("Enter a software requirement: ")

    print("\nGenerated test scenarios:")
    for case in generate_test_cases(requirement):
        print(f"- {case}")


if __name__ == "__main__":
    main()
