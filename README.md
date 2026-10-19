
# AI Multi-Agent QA Assistant

A Python-based QA assistant prototype for rule-based structured test-case generation, automated unit testing, and continuous integration.

![Python QA Tests](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions/workflows/python-tests.yml/badge.svg)

## Project Status

**Current version:** Version 3 — Rule-Based QA Assistant

| Feature | Status |
|---|---|
| Basic test-case generation | Completed |
| Structured test-case generation | Completed |
| Automated unit tests | 8 tests passing |
| GitHub Actions CI | Configured |
| Real AI model integration | Planned |
| API testing assistance | Planned |
| Test automation script generation | Planned |

## Features

- Generate test cases from software requirements.
- Support legacy string-based test-case generation.
- Generate structured test cases with test IDs, scenarios, and expected results.
- Handle empty and whitespace-only requirements.
- Run automated tests using Python's built-in `unittest` framework.
- Automatically execute unit tests using GitHub Actions.
- Run locally without an API key or third-party Python packages.

## Technology Stack

- Python 3
- `unittest`
- Git and GitHub
- GitHub Actions

## Project Structure

```text
AI-MultiAgent-QA-Assistant/
├── qa_assistant.py
├── test_qa_assistant.py
├── README.md
└── .github/
    └── workflows/
        └── python-tests.yml
```

## Requirements

- Python 3.10 or later
- No third-party Python packages required
- No API key required

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant.git
cd AI-MultiAgent-QA-Assistant
```

### 2. Run the assistant

```bash
python qa_assistant.py
```

Enter a software requirement when prompted.

Example:

```text
User login with email and password
```

## Sample Output

For a valid requirement, the assistant generates five structured test cases.

Example format:

```text
Test ID: TC01
Scenario: Verify the main flow
Expected Result: The requirement is processed successfully with valid input.
--------------------------------------------------
Test ID: TC02
Scenario: Verify invalid input handling
Expected Result: Invalid input is rejected and a clear validation message is shown.
--------------------------------------------------
```

The actual expected results are generic examples and should be reviewed against the application's requirements.

## Automated Testing

Run the unit tests locally:

```bash
python -m unittest -v test_qa_assistant.py
```

The current test suite contains eight unit tests covering:

- Empty requirements
- Whitespace-only requirements
- Valid requirement handling
- Legacy string-based output
- Structured output fields

### Continuous Integration

GitHub Actions automatically runs the tests when code is pushed to `main`, when a pull request targets `main`, or when the workflow is triggered manually.

**Latest verified result:** 8 unit tests passed.

[View GitHub Actions](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions)

## Current Limitations

- Test cases are generated using predefined rules rather than a real AI model.
- The project does not yet implement autonomous multi-agent behaviour.
- Expected results are generic and need QA review.
- The current version does not execute the generated test cases against a real application.

## Roadmap

- [ ] Add more unit tests for invalid and boundary inputs.
- [ ] Improve requirement-based test-case generation.
- [ ] Explore API testing assistance.
- [ ] Generate automation scripts.
- [ ] Evaluate AI model integration options.
- [ ] Explore multi-agent QA workflows.

## About This Project

This project explores how Python and automated testing can support software quality assurance. It is a learning and portfolio project that will evolve through additional testing capabilities and future AI integration.

## Author

Geetha A.

Software QA | Manual Testing | API Testing | Python | AI-Assisted QA
