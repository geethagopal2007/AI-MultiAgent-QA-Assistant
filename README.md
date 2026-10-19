
# AI Multi-Agent QA Assistant

A Python-based QA assistant prototype that generates software test cases from requirements. Version 3 uses rule-based generation and does not require an API key or external AI service.

![Python QA Tests](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions/workflows/python-tests.yml/badge.svg)

## Features

- Generate test cases from software requirements.
- Support legacy string-based test-case generation.
- Generate structured test cases with test IDs, scenarios, and expected results.
- Handle empty and whitespace-only requirements.
- Run automated unit tests using Python's built-in `unittest`.
- Automatically execute tests through GitHub Actions.

## Technology Stack

- Python 3
- `unittest`
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

## Run the Assistant

Clone the repository:

```bash
git clone https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant.git
cd AI-MultiAgent-QA-Assistant
```

Run the application:

```bash
python qa_assistant.py
```

Enter a software requirement when prompted. The assistant generates five structured test cases.

Example requirement:

```text
User login with email and password
```

## Run Automated Tests

Run the test suite:

```bash
python -m unittest -v test_qa_assistant.py
```

The current test suite contains eight unit tests covering legacy and structured test-case generation.

## Continuous Integration

GitHub Actions automatically runs unit tests when code is pushed to `main`, when a pull request targets `main`, or when the workflow is triggered manually.

View the [Python QA Tests workflow](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions/workflows/python-tests.yml).

## Current Limitations

- Test cases are generated using predefined rules.
- No real AI model or autonomous multi-agent system is integrated yet.
- Expected results are generic and must be validated against actual software requirements.
- Generated test cases are suggestions and require QA review.

## Future Enhancements

- Integrate an AI model for requirement analysis.
- Add API testing assistance.
- Generate automation scripts.
- Introduce test prioritization and reporting.
- Explore multi-agent QA workflows.

## Author

Geetha A.

Software QA | Manual Testing | API Testing | Python | AI-Assisted QA
