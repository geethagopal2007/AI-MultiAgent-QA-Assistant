
import os
import json
import html
import requests
import pandas as pd
import streamlit as st

from live_api_tester import run_live_api_test


# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="AI Multi-Agent QA Assistant",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Multi-Agent QA Assistant")
st.caption("Live API Testing • AI Test Case Generation • Test Reports")


# -------------------- SESSION STATE --------------------

if "api_test_history" not in st.session_state:
    st.session_state.api_test_history = []

if "generated_test_cases" not in st.session_state:
    st.session_state.generated_test_cases = []


# -------------------- API KEY --------------------

def get_api_key():
    """Read OpenAI key from Streamlit Secrets or environment."""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("OPENAI_API_KEY", "")


# -------------------- FREE TEST CASE GENERATOR --------------------

def generate_template_test_cases(
    endpoint,
    method,
    description,
    required_fields,
    count=7,
):
    """
    Generate test cases locally without an external AI API.
    These are template-based QA cases, not AI-generated cases.
    """

    fields = ", ".join(required_fields) or "expected response fields"
    method = method.upper()

    templates = [
        {
            "scenario": "Valid request",
            "test_type": "Positive",
            "steps": f"Send a valid {method} request to {endpoint}.",
            "expected_result": (
                "The API returns the expected successful response."
            ),
            "priority": "High",
        },
        {
            "scenario": "Invalid endpoint",
            "test_type": "Negative",
            "steps": (
                "Send a request to an invalid or unknown endpoint."
            ),
            "expected_result": (
                "The API returns an appropriate error response."
            ),
            "priority": "High",
        },
        {
            "scenario": "Unsupported HTTP method",
            "test_type": "Negative",
            "steps": (
                f"Send an unsupported HTTP method to {endpoint}."
            ),
            "expected_result": (
                "The API rejects the method appropriately."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Required response fields",
            "test_type": "Validation",
            "steps": f"Check that the response contains: {fields}.",
            "expected_result": (
                "All specified fields are present and have "
                "appropriate values and data types."
            ),
            "priority": "High",
        },
        {
            "scenario": "Response time",
            "test_type": "Performance",
            "steps": (
                "Send the request and measure its response time."
            ),
            "expected_result": (
                "The response time meets the agreed performance SLA."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Empty or missing input",
            "test_type": "Boundary",
            "steps": (
                "Where applicable, submit the request with required "
                "inputs missing or empty."
            ),
            "expected_result": (
                "The API validates missing inputs appropriately."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Authentication check",
            "test_type": "Security",
            "steps": (
                "For a protected endpoint, send a request without "
                "valid authentication credentials."
            ),
            "expected_result": (
                "Unauthorized requests are rejected and protected "
                "data is not disclosed."
            ),
            "priority": "High",
        },
        {
            "scenario": "Malformed JSON",
            "test_type": "Negative",
            "steps": (
                "For an endpoint accepting JSON, submit malformed "
                "JSON in the request body."
            ),
            "expected_result": (
                "The API handles malformed JSON with an appropriate "
                "validation error."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Content-Type validation",
            "test_type": "Validation",
            "steps": (
                "Where applicable, send a request with an incorrect "
                "or missing Content-Type header."
            ),
            "expected_result": (
                "The API accepts supported content types and handles "
                "unsupported types appropriately."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Response content type",
            "test_type": "Validation",
            "steps": "Inspect the response Content-Type header.",
            "expected_result": (
                "The response content type matches the documented "
                "API response format."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "Repeated request",
            "test_type": "Reliability",
            "steps": (
                "Repeat the same valid request under normal conditions."
            ),
            "expected_result": (
                "The API behaves consistently for equivalent requests."
            ),
            "priority": "Medium",
        },
        {
            "scenario": "HTTP status validation",
            "test_type": "Validation",
            "steps": (
                "Check the returned HTTP status against the "
                "expected status for the request."
            ),
            "expected_result": (
                "The HTTP status matches the documented API behaviour."
            ),
            "priority": "High",
        },
        {
            "scenario": "Response structure",
            "test_type": "Validation",
            "steps": (
                "Inspect the response structure and data types."
            ),
            "expected_result": (
                "The response follows the documented schema."
            ),
            "priority": "High",
        },
        {
            "scenario": "Unexpected query parameters",
            "test_type": "Negative",
            "steps": (
                "Where applicable, send an unexpected or invalid "
                "query parameter."
            ),
            "expected_result": (
                "The API handles unsupported parameters consistently "
                "with its specification."
            ),
            "priority": "Low",
        },
        {
            "scenario": "Business requirement review",
            "test_type": "Functional",
            "steps": (
                "Compare the response with the described requirement: "
                f"{description or 'No description provided'}"
            ),
            "expected_result": (
                "The response satisfies the stated requirement. "
                "Confirm any undocumented assumptions with the API owner."
            ),
            "priority": "High",
        },
    ]

    cases = []
    for index, template in enumerate(templates[:count], start=1):
        cases.append(
            {
                "test_case_id": f"TC{index:03d}",
                "scenario": template["scenario"],
                "test_type": template["test_type"],
                "steps": template["steps"],
                "expected_result": template["expected_result"],
                "priority": template["priority"],
            }
        )

    return cases


# -------------------- AI TEST CASE GENERATOR --------------------

def generate_ai_test_cases(
    endpoint,
    method,
    description,
    required_fields,
    count,
):
    """
    Try OpenAI first. If no API key is configured, use free templates.
    API/network errors are handled by the calling section.
    """

    api_key = get_api_key()

    if not api_key:
        return (
            generate_template_test_cases(
                endpoint,
                method,
                description,
                required_fields,
                count,
            ),
            "Free template fallback",
        )

    prompt = f"""
Generate exactly {count} practical API test cases.

Endpoint: {endpoint}
HTTP method: {method}
Description: {description or "Not provided"}
Required JSON fields: {", ".join(required_fields) or "Not specified"}

Include a useful mix of positive, negative, boundary, validation,
security and performance scenarios where applicable.

Do not assume undocumented API behaviour. State assumptions clearly.
Do not execute any tests. Only generate test case definitions.

Return valid JSON in this format:
{{
  "test_cases": [
    {{
      "test_case_id": "TC001",
      "scenario": "Scenario name",
      "test_type": "Positive",
      "steps": "Test steps",
      "expected_result": "Expected behaviour",
      "priority": "High"
    }}
  ]
}}
"""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an experienced API QA engineer. "
                        "Return only valid JSON matching the schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        },
        timeout=45,
    )

    response.raise_for_status()

    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    raw_cases = parsed.get("test_cases", [])

    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("The AI returned no valid test cases.")

    clean_cases = []

    for index, case in enumerate(raw_cases[:count], start=1):
        if not isinstance(case, dict):
            continue

        clean_cases.append(
            {
                "test_case_id": str(
                    case.get("test_case_id", f"TC{index:03d}")
                ),
                "scenario": str(case.get("scenario", "")),
                "test_type": str(case.get("test_type", "")),
                "steps": str(case.get("steps", "")),
                "expected_result": str(
                    case.get("expected_result", "")
                ),
                "priority": str(case.get("priority", "Medium")),
            }
        )

    if not clean_cases:
        raise ValueError("No usable test cases were returned.")

    return clean_cases, "OpenAI AI generation"


# -------------------- HTML REPORT --------------------

def build_html_report(history):
    rows = []

    for item in history:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('test_id', '')))}</td>"
            f"<td>{html.escape(str(item.get('status', '')))}</td>"
            f"<td>{html.escape(str(item.get('message', '')))}</td>"
            f"<td>{html.escape(str(item.get('url', '')))}</td>"
            "</tr>"
        )

    passed = sum(
        item.get("status") == "PASS" for item in history
    )
    failed = len(history) - passed

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>API Test Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #17365d; color: white; }}
</style>
</head>
<body>
<h1>API Test Report</h1>
<p>Total: {len(history)} | Passed: {passed} | Failed: {failed}</p>
<table>
<thead>
<tr><th>Test ID</th><th>Status</th><th>Message</th><th>URL</th></tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</body>
</html>
"""


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.header("⚙️ Test Configuration")

    timeout = st.number_input(
        "Timeout (seconds)",
        min_value=1,
        max_value=120,
        value=10,
    )

    expected_status = st.number_input(
        "Expected HTTP status",
        min_value=100,
        max_value=599,
        value=200,
    )


# -------------------- TABS --------------------

tab_api, tab_ai, tab_history = st.tabs(
    [
        "🚀 Live API Testing",
        "🤖 AI Test Case Generator",
        "📊 Test History & Reports",
    ]
)


# -------------------- LIVE API TESTING --------------------

with tab_api:
    st.subheader("Run a Live API Test")

    url = st.text_input(
        "API endpoint URL",
        value="https://jsonplaceholder.typicode.com/users/1",
        key="api_endpoint",
        help="Enter a valid HTTP or HTTPS API endpoint.",
    )

    required_fields_text = st.text_input(
        "Required JSON fields (comma-separated)",
        value="id,name,email",
        key="api_required_fields",
    )

    if st.button("🚀 Run API Test", type="primary"):
        required_fields = [
            field.strip()
            for field in required_fields_text.split(",")
            if field.strip()
        ]

        if not url.strip().startswith(("http://", "https://")):
            st.error("Enter a valid HTTP or HTTPS URL.")
        else:
            try:
                with st.spinner("Testing API endpoint..."):
                    result = run_live_api_test(
                        url.strip(),
                        expected_status=int(expected_status),
                        required_fields=required_fields,
                        timeout=float(timeout),
                    )

                if not isinstance(result, dict):
                    raise TypeError(
                        "run_live_api_test must return a dictionary."
                    )

                result = dict(result)
                result.setdefault(
                    "test_id",
                    f"API_{len(st.session_state.api_test_history) + 1:03d}",
                )
                result.setdefault("url", url.strip())
                result.setdefault("status", "FAIL")
                result.setdefault(
                    "message", "No result message returned."
                )
                result.setdefault("status_code", None)
                result.setdefault("response_time_ms", None)

                st.session_state.api_test_history.append(result)

                if result["status"] == "PASS":
                    st.success("API test passed!")
                else:
                    st.error("API test failed.")

                st.json(result)

            except (TypeError, ValueError) as exc:
                st.error(f"Invalid input or test result: {exc}")
            except Exception as exc:
                st.error(f"Unable to run API test: {exc}")


# -------------------- TEST CASE GENERATOR --------------------

with tab_ai:
    st.subheader("🤖 API Test Case Generator")

    st.write(
        "Generate test cases from an endpoint, HTTP method, "
        "description and expected response fields."
    )

    st.info(
        "Free fallback is available without OpenAI API credits. "
        "Fallback cases use predefined QA templates, not an AI model."
    )

    ai_endpoint = st.text_input(
        "API endpoint",
        value="https://jsonplaceholder.typicode.com/users/1",
        key="ai_endpoint",
    )

    ai_method = st.selectbox(
        "HTTP method",
        ["GET", "POST", "PUT", "PATCH", "DELETE"],
        key="ai_method",
    )

    ai_description = st.text_area(
        "API description / requirements",
        value="Fetch a user and return the user's id, name and email.",
        key="ai_description",
        help="Describe the expected API behaviour and business rules.",
    )

    ai_fields_text = st.text_input(
        "Expected response fields",
        value="id,name,email",
        key="ai_fields",
    )

    ai_count = st.slider(
        "Number of test cases",
        min_value=3,
        max_value=15,
        value=7,
        key="ai_count",
    )

    if st.button("✨ Generate Test Cases", type="primary"):
        ai_fields = [
            field.strip()
            for field in ai_fields_text.split(",")
            if field.strip()
        ]

        if not ai_endpoint.strip().startswith(
            ("http://", "https://")
        ):
            st.error("Enter a valid HTTP or HTTPS endpoint.")
        else:
            try:
                with st.spinner("Generating test cases..."):
                    try:
                        cases, generation_mode = generate_ai_test_cases(
                            endpoint=ai_endpoint.strip(),
                            method=ai_method,
                            description=ai_description.strip(),
                            required_fields=ai_fields,
                            count=int(ai_count),
                        )

                    except Exception as api_error:
                        # Any API failure falls back to free templates.
                        cases = generate_template_test_cases(
                            endpoint=ai_endpoint.strip(),
                            method=ai_method,
                            description=ai_description.strip(),
                            required_fields=ai_fields,
                            count=int(ai_count),
                        )
                        generation_mode = "Free template fallback"
                        fallback_reason = (
                            f"{type(api_error).__name__}: {api_error}"
                        )
                    else:
                        fallback_reason = None

                st.session_state.generated_test_cases = cases

                if generation_mode == "OpenAI AI generation":
                    st.success(
                        f"Generated {len(cases)} test cases using OpenAI."
                    )
                else:
                    st.warning(
                        f"Generated {len(cases)} free template-based "
                        "test cases. OpenAI was not used."
                    )
                    if fallback_reason:
                        st.caption(
                            "Fallback reason: " + fallback_reason
                        )

                st.caption(f"Generation mode: {generation_mode}")

            except Exception as exc:
                st.error(f"Test case generation failed: {exc}")

    # Show generated cases and download buttons.
    if st.session_state.generated_test_cases:
        st.subheader("Generated Test Cases")

        cases_df = pd.DataFrame(
            st.session_state.generated_test_cases
        )

        st.dataframe(cases_df, use_container_width=True)

        st.download_button(
            "⬇️ Download Test Cases (CSV)",
            data=cases_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="ai_generated_test_cases.csv",
            mime="text/csv",
        )

        st.download_button(
            "⬇️ Download Test Cases (JSON)",
            data=json.dumps(
                st.session_state.generated_test_cases,
                indent=2,
                ensure_ascii=False,
            ).encode("utf-8"),
            file_name="ai_generated_test_cases.json",
            mime="application/json",
        )

        st.caption(
            "These are test definitions only. They have not been "
            "executed against the API."
        )


# -------------------- TEST HISTORY AND REPORTS --------------------

with tab_history:
    st.subheader("📊 Test Summary")

    history = st.session_state.api_test_history

    if history:
        total = len(history)
        passed = sum(
            item.get("status") == "PASS" for item in history
        )
        failed = total - passed

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tests", total)
        col2.metric("Passed", passed)
        col3.metric("Failed", failed)

        st.subheader("Test History")

        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8-sig")

        json_data = json.dumps(
            history,
            indent=2,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

        html_data = build_html_report(history).encode("utf-8")

        st.subheader("📥 Download Reports")

        c1, c2, c3 = st.columns(3)

        c1.download_button(
            "Download CSV",
            data=csv_data,
            file_name="api_test_report.csv",
            mime="text/csv",
        )

        c2.download_button(
            "Download JSON",
            data=json_data,
            file_name="api_test_report.json",
            mime="application/json",
        )

        c3.download_button(
            "Download HTML",
            data=html_data,
            file_name="api_test_report.html",
            mime="text/html",
        )

        if st.button("Clear Test History"):
            st.session_state.api_test_history = []
            st.rerun()

    else:
        st.info("No API tests have been run in this session yet.")

    if st.session_state.generated_test_cases:
        st.divider()
        st.subheader("Latest Generated Test Cases")
        st.dataframe(
            pd.DataFrame(st.session_state.generated_test_cases),
            use_container_width=True,
        )
