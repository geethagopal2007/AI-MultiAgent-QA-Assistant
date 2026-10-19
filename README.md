# AI Multi-Agent QA Assistant

**A Python-based QA automation project for structured test-case generation, API response validation, and automated test reporting.**

[![Python Tests](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions/workflows/python-tests.yml/badge.svg)](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant/actions/workflows/python-tests.yml)

## Overview

AI Multi-Agent QA Assistant is a portfolio project focused on improving software quality assurance workflows using Python.

The project currently provides rule-based test-case generation, reusable API validation helpers, automated unit tests, and exportable test reports. It is being developed incrementally toward a more advanced AI-assisted QA system.

## Features

### 1. Test Case Generation
- Generate structured QA test scenarios from requirements.
- Validate required fields in generated test cases.
- Handle empty and whitespace-only inputs.
- Support legacy test-case generation.

### 2. API Response Validation
- Validate HTTP response status codes.
- Check required JSON fields and expected values.
- Validate nested JSON fields using dot-separated paths.
- Check JSON field types, including correct handling of Boolean and integer values.
- Validate common HTTP error status codes.

### 3. API Test Scenario Generation
Generate basic scenarios for:
- Successful API responses.
- Required JSON fields and expected values.
- API error responses.

### 4. Test Report Generation
Generate a summary of test results, including total, passed, and failed tests.

Export reports in three formats:
- **HTML** — view test results in a browser.
- **CSV** — open test results in spreadsheet applications.
- **JSON** — use structured test results in other tools or workflows.

### 5. Automated Testing with GitHub Actions
The repository uses GitHub Actions to run Python unit tests when changes are pushed to the repository.

## Technology Stack

- Python
- Python standard library
- `unittest`
- Git and GitHub
- GitHub Actions
- HTML, CSV, and JSON

## Project Structure

```text
AI-MultiAgent-QA-Assistant/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── README.md
├── qa_assistant.py
├── test_qa_assistant.py
├── api_test_assistant.py
└── test_api_test_assistant.py
```

## Getting Started

### Prerequisites

- Python 3.10 or later recommended
- Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant.git
cd AI-MultiAgent-QA-Assistant
```

### 2. Run the unit tests

```bash
python -m unittest -v test_qa_assistant.py
```

Run the API validation and report tests:

```bash
python -m unittest -v test_api_test_assistant.py
```

Run all discovered unit tests:

```bash
python -m unittest discover -v
```

## Example: Validate an API Response

```python
from api_test_assistant import (
    validate_api_response,
    validate_json_fields,
    validate_json_field_types,
)

status_ok = validate_api_response(200)

data = {
    "user": {
        "id": 101,
        "name": "Geetha",
        "active": True,
    }
}

fields_ok = validate_json_fields(
    data,
    ["user.id", "user.name"],
)

types_ok = validate_json_field_types(
    data,
    {
        "user.id": int,
        "user.name": str,
        "user.active": bool,
    },
)

print("Status valid:", status_ok)
print("Required fields valid:", fields_ok)
print("Field types valid:", types_ok)
```

## Example: Generate Test Reports

```python
from api_test_assistant import (
    generate_test_report,
    generate_html_report,
    export_test_report_csv,
    export_test_report_json,
)

results = [
    {
        "test_id": "API01",
        "status": "PASS",
        "message": "HTTP 200 received",
    },
    {
        "test_id": "API02",
        "status": "FAIL",
        "message": "Required email field is missing",
    },
]

summary = generate_test_report(results)
print(summary)

generate_html_report(results)
export_test_report_csv(results)
export_test_report_json(results)
```

The default output files are:

- `api_test_report.html`
- `api_test_report.csv`
- `api_test_report.json`

Run the example from a directory where you have permission to create files.

## Quality Assurance Approach

This project demonstrates practical QA concepts, including:

- Positive and negative test scenarios.
- Input validation and edge-case handling.
- Nested JSON validation.
- Type validation.
- Unit testing and regression testing.
- Automated test execution through CI.
- Structured reporting of test outcomes.

## Roadmap

Planned improvements include:

- Expand automated API test coverage.
- Add more robust error handling and report validation.
- Integrate real HTTP requests for endpoint testing.
- Introduce AI-assisted test-case generation.
- Develop a genuine multi-agent architecture for requirement analysis, test generation, and test review.

## Project Status

**Active learning and development project.**

The current implementation focuses on rule-based QA utilities, API validation, reporting, and automated unit tests. AI-assisted and multi-agent capabilities are planned enhancements rather than completed features.

## Author

**Geetha A.**

Software QA and testing professional exploring Python automation, API testing, and AI-assisted quality engineering.

## Repository

[View AI Multi-Agent QA Assistant on GitHub](https://github.com/geethagopal2007/AI-MultiAgent-QA-Assistant)
