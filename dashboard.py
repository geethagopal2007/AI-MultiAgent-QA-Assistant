
import os
import json
import html
import requests
import pandas as pd
import streamlit as st

from live_api_tester import (
    run_live_api_test,
    run_api_test_case,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Multi-Agent QA Assistant",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Multi-Agent QA Assistant")
st.caption(
    "Live API Testing • Test Case Generation • "
    "Automated Execution • Test Reports"
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "api_test_history": [],
    "generated_test_cases": [],
    "execution_results": [],
    "generation_mode": "",
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =========================================================
# API KEY
# =========================================================

def get_api_key():
    """Read the OpenAI API key from Streamlit Secrets or environment."""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("OPENAI_API_KEY", "")


# =========================================================
# FREE TEMPLATE TEST CASE GENERATOR
# =========================================================

def generate_template_test_cases(
    endpoint,
    method,
    description,
    required_fields,
    count=7,
):
    """Generate test case definitions without an AI API."""

    fields = ", ".join(required_fields) or "response fields"
    method = method.upper()

    templates = [
        {
            "scenario": "Valid request",
            "test_type": "Positive",
            "steps": f"Send a valid {method} request to {endpoint}.",
            "expected_result": "The API returns the expected successful response.",
            "priority": "High",
        },
        {
            "scenario": "Invalid endpoint",
            "test_type": "Negative",
            "steps": "Request an invalid or unknown endpoint.",
            "expected_result": "The server returns an appropriate error response.",
            "priority": "High",
        },
        {
            "scenario": "Unsupported HTTP method",
            "test_type": "Negative",
            "steps": f"Try an unsupported HTTP method on {endpoint}.",
            "expected_result": "The API handles the unsupported method appropriately.",
            "priority": "Medium",
        },
        {
            "scenario": "Required response fields",
            "test_type": "Validation",
            "steps": f"Check the response for these fields: {fields}.",
            "expected_result": "All required fields are present.",
            "priority": "High",
        },
        {
            "scenario": "Response time",
            "test_type": "Performance",
            "steps": "Send a request and measure its response time.",
            "expected_result": "Response time meets the agreed performance target.",
            "priority": "Medium",
        },
        {
            "scenario": "Authentication check",
            "test_type": "Security",
            "steps": "For a protected endpoint, test a request without valid credentials.",
            "expected_result": "Unauthorised access is rejected.",
            "priority": "High",
        },
        {
            "scenario": "Response structure",
            "test_type": "Validation",
            "steps": "Inspect the response structure and data types.",
            "expected_result": "The response matches the documented API schema.",
            "priority": "High",
        },
        {
            "scenario": "Malformed JSON",
            "test_type": "Negative",
            "steps": "Where applicable, submit malformed JSON to the API.",
            "expected_result": "The API handles invalid JSON appropriately.",
            "priority": "Medium",
        },
        {
            "scenario": "Repeated request",
            "test_type": "Reliability",
            "steps": "Repeat the same request under normal conditions.",
            "expected_result": "Equivalent requests behave consistently.",
            "priority": "Medium",
        },
        {
            "scenario": "HTTP status validation",
            "test_type": "Validation",
            "steps": "Compare the returned HTTP status with the expected status.",
            "expected_result": "The status matches the documented behaviour.",
            "priority": "High",
        },
        {
            "scenario": "Content type validation",
            "test_type": "Validation",
            "steps": "Inspect the response Content-Type header.",
            "expected_result": "The response uses the expected content type.",
            "priority": "Medium",
        },
        {
            "scenario": "Boundary input",
            "test_type": "Boundary",
            "steps": "Where applicable, test empty, missing or boundary input values.",
            "expected_result": "Input validation follows the API specification.",
            "priority": "Medium",
        },
        {
            "scenario": "Unexpected query parameter",
            "test_type": "Negative",
            "steps": "Where applicable, send an unsupported query parameter.",
            "expected_result": "The API handles the parameter consistently.",
            "priority": "Low",
        },
        {
            "scenario": "Business requirement review",
            "test_type": "Functional",
            "steps": f"Compare the response with this requirement: {description}",
            "expected_result": "The response satisfies the documented requirement.",
            "priority": "High",
        },
        {
            "scenario": "Response field values",
            "test_type": "Validation",
            "steps": f"Inspect the values and types of: {fields}.",
            "expected_result": "Field values and data types are valid.",
            "priority": "High",
        },
    ]

    cases = []

    for index, template in enumerate(templates[:count], start=1):
        cases.append({
            "test_case_id": f"TC{index:03d}",
            **template,
        })

    return cases


# =========================================================
# AI TEST CASE GENERATOR WITH FREE FALLBACK
# =========================================================

def generate_ai_test_cases(
    endpoint,
    method,
    description,
    required_fields,
    count,
):
    """Try OpenAI first; use local templates if no key is configured."""

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
Generate exactly {count} API test case definitions.

Endpoint: {endpoint}
HTTP method: {method}
Requirements: {description}
Expected response fields: {", ".join(required_fields)}

Include positive, negative, validation, boundary and security scenarios
where appropriate. Do not assume undocumented behaviour.

Return valid JSON in this format:
{{
  "test_cases": [
    {{
      "test_case_id": "TC001",
      "scenario": "Valid request",
      "test_type": "Positive",
      "steps": "Test steps",
      "expected_result": "Expected result",
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
                        "You are an API QA engineer. "
                        "Return only valid JSON."
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
        raise ValueError("The AI returned no test cases.")

    cases = []

    for index, case in enumerate(raw_cases[:count], start=1):
        if not isinstance(case, dict):
            continue

        cases.append({
            "test_case_id": str(
                case.get("test_case_id", f"TC{index:03d}")
            ),
            "scenario": str(case.get("scenario", "")),
            "test_type": str(case.get("test_type", "")),
            "steps": str(case.get("steps", "")),
            "expected_result": str(case.get("expected_result", "")),
            "priority": str(case.get("priority", "Medium")),
        })

    if not cases:
        raise ValueError("No usable test cases were returned.")

    return cases, "OpenAI AI generation"


# =========================================================
# HTML REPORT
# =========================================================

def build_html_report(results):
    rows = []

    for item in results:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('test_id', '')))}</td>"
            f"<td>{html.escape(str(item.get('scenario', '')))}</td>"
            f"<td>{html.escape(str(item.get('status', '')))}</td>"
            f"<td>{html.escape(str(item.get('status_code', '')))}</td>"
            f"<td>{html.escape(str(item.get('message', '')))}</td>"
            "</tr>"
        )

    passed = sum(item.get("status") == "PASS" for item in results)
    failed = len(results) - passed

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>API Test Execution Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #17365d; color: white; }}
</style>
</head>
<body>
<h1>API Test Execution Report</h1>
<p>Total: {len(results)} | Passed: {passed} | Failed: {failed}</p>
<table>
<thead>
<tr>
<th>Test ID</th><th>Scenario</th><th>Status</th>
<th>HTTP Status</th><th>Message</th>
</tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</body>
</html>"""


# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================

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


# =========================================================
# APPLICATION TABS
# =========================================================

tab_api, tab_ai, tab_history = st.tabs([
    "🚀 Live API Testing",
    "🤖 AI Test Case Generator",
    "📊 Test History & Reports",
])


# =========================================================
# TAB 1: LIVE API TESTING
# =========================================================

with tab_api:
    st.subheader("Run a Live API Test")

    url = st.text_input(
        "API endpoint URL",
        value="https://jsonplaceholder.typicode.com/users/1",
        key="api_endpoint",
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
                result.setdefault("message", "No result message returned.")
                result.setdefault("status_code", None)
                result.setdefault("response_time_ms", None)

                st.session_state.api_test_history.append(result)

                if result["status"] == "PASS":
                    st.success("API test passed!")
                else:
                    st.error("API test failed.")

                st.json(result)

            except Exception as exc:
                st.error(f"Unable to run API test: {exc}")


# =========================================================
# TAB 2: GENERATE AND EXECUTE TEST CASES
# =========================================================

with tab_ai:
    st.subheader("🤖 API Test Case Generator")

    st.write(
        "Generate test cases from an endpoint, HTTP method, "
        "description and expected response fields."
    )

    st.info(
        "Free template fallback works without OpenAI API credits. "
        "Template cases are not generated by an AI model."
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
        if not ai_endpoint.strip().startswith(("http://", "https://")):
            st.error("Enter a valid HTTP or HTTPS endpoint.")
        else:
            ai_fields = [
                field.strip()
                for field in ai_fields_text.split(",")
                if field.strip()
            ]

            fallback_reason = None

            with st.spinner("Generating test cases..."):
                try:
                    cases, generation_mode = generate_ai_test_cases(
                        endpoint=ai_endpoint.strip(),
                        method=ai_method,
                        description=ai_description.strip(),
                        required_fields=ai_fields,
                        count=int(ai_count),
                    )
                except Exception as exc:
                    cases = generate_template_test_cases(
                        endpoint=ai_endpoint.strip(),
                        method=ai_method,
                        description=ai_description.strip(),
                        required_fields=ai_fields,
                        count=int(ai_count),
                    )
                    generation_mode = "Free template fallback"
                    fallback_reason = f"{type(exc).__name__}: {exc}"

            st.session_state.generated_test_cases = cases
            st.session_state.execution_results = []
            st.session_state.generation_mode = generation_mode

            if generation_mode == "OpenAI AI generation":
                st.success(f"Generated {len(cases)} AI test cases.")
            else:
                st.warning(
                    f"Generated {len(cases)} template-based test cases."
                )
                if fallback_reason:
                    st.caption("Fallback reason: " + fallback_reason)

            st.caption(f"Generation mode: {generation_mode}")

    # Display generated cases and execution controls.
    if st.session_state.generated_test_cases:
        st.divider()
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
            key="download_cases_csv",
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
            key="download_cases_json",
        )

        st.divider()
        st.subheader("▶️ Execute Test Cases")

        st.warning(
            "This initial runner sends each case to the same endpoint "
            "with the selected HTTP method and validates HTTP status "
            "and required response fields. It does not yet perform "
            "scenario-specific negative tests."
        )

        if st.button(
            "▶️ Run All Test Cases",
            type="primary",
            key="run_all_test_cases",
        ):
            execution_results = []

            fields_to_check = [
                field.strip()
                for field in ai_fields_text.split(",")
                if field.strip()
            ]

            cases_to_run = st.session_state.generated_test_cases

            progress = st.progress(0)

            with st.spinner("Executing API test cases..."):
                for index, case in enumerate(cases_to_run):
                    try:
                        result = run_api_test_case(
                            test_case=case,
                            url=ai_endpoint.strip(),
                            method=ai_method,
                            required_fields=fields_to_check,
                            timeout=float(timeout),
                            expected_status=int(expected_status),
                        )

                        if not isinstance(result, dict):
                            result = {
                                "status": "FAIL",
                                "message": "Runner returned an invalid result.",
                            }
                        else:
                            result = dict(result)

                    except Exception as exc:
                        result = {
                            "status": "FAIL",
                            "message": f"{type(exc).__name__}: {exc}",
                            "status_code": None,
                            "response_time_ms": None,
                        }

                    result["test_id"] = case.get(
                        "test_case_id",
                        f"TC{index + 1:03d}",
                    )
                    result["scenario"] = case.get("scenario", "Test case")
                    result.setdefault("status", "FAIL")
                    result.setdefault("status_code", None)
                    result.setdefault("response_time_ms", None)
                    result.setdefault("message", "")

                    execution_results.append(result)
                    progress.progress((index + 1) / len(cases_to_run))

            st.session_state.execution_results = execution_results

        # Results are shown after execution and remain visible on reruns.
        if st.session_state.execution_results:
            results = st.session_state.execution_results

            passed = sum(
                str(item.get("status", "")).upper() == "PASS"
                for item in results
            )
            failed = len(results) - passed

            st.subheader("📊 Execution Summary")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Executed", len(results))
            col2.metric("PASS", passed)
            col3.metric("FAIL", failed)

            results_df = pd.DataFrame(results)
            st.subheader("Execution Results")

            display_columns = [
                column for column in [
                    "test_id",
                    "scenario",
                    "status",
                    "status_code",
                    "response_time_ms",
                    "message",
                ]
                if column in results_df.columns
            ]

            st.dataframe(
                results_df[display_columns],
                use_container_width=True,
            )

            st.download_button(
                "⬇️ Download Execution Results (CSV)",
                data=results_df.to_csv(
                    index=False
                ).encode("utf-8-sig"),
                file_name="api_execution_results.csv",
                mime="text/csv",
                key="download_results_csv",
            )

            st.download_button(
                "⬇️ Download Execution Results (JSON)",
                data=json.dumps(
                    results,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                ).encode("utf-8"),
                file_name="api_execution_results.json",
                mime="application/json",
                key="download_results_json",
            )

            st.download_button(
                "⬇️ Download Execution Report (HTML)",
                data=build_html_report(results).encode("utf-8"),
                file_name="api_execution_report.html",
                mime="text/html",
                key="download_results_html",
            )

            st.caption(
                "PASS/FAIL reflects the validations implemented by "
                "the current API runner, not every scenario described "
                "in the generated test case."
            )


# =========================================================
# TAB 3: TEST HISTORY AND REPORTS
# =========================================================

with tab_history:
    st.subheader("📊 Test Summary")

    history = st.session_state.api_test_history

    if history:
        total = len(history)
        passed = sum(
            item.get("status") == "PASS"
            for item in history
        )
        failed = total - passed

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tests", total)
        col2.metric("Passed", passed)
        col3.metric("Failed", failed)

        st.subheader("Test History")

        history_df = pd.DataFrame(history)
        st.dataframe(history_df, use_container_width=True)

        st.subheader("📥 Download History Reports")

        col1, col2, col3 = st.columns(3)

        col1.download_button(
            "Download CSV",
            data=history_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="api_test_report.csv",
            mime="text/csv",
            key="history_csv",
        )

        col2.download_button(
            "Download JSON",
            data=json.dumps(
                history,
                indent=2,
                ensure_ascii=False,
                default=str,
            ).encode("utf-8"),
            file_name="api_test_report.json",
            mime="application/json",
            key="history_json",
        )

        col3.download_button(
            "Download HTML",
            data=build_html_report(history).encode("utf-8"),
            file_name="api_test_report.html",
            mime="text/html",
            key="history_html",
        )

        if st.button("🗑️ Clear Test History"):
            st.session_state.api_test_history = []
            st.rerun()

    else:
        st.info("No live API tests have been run in this session yet.")

    if st.session_state.generated_test_cases:
        st.divider()
        st.subheader("Latest Generated Test Cases")
        st.dataframe(
            pd.DataFrame(st.session_state.generated_test_cases),
            use_container_width=True,
        )
