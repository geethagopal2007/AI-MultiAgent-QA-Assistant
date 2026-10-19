
"""
AI Multi-Agent QA Assistant - Web Dashboard
Run with: streamlit run dashboard.py
"""

import json
import tempfile
from pathlib import Path

import streamlit as st

from live_api_tester import (
    run_live_api_test,
    export_live_api_html,
    export_live_api_csv,
    export_live_api_json,
)


st.set_page_config(
    page_title="AI Multi-Agent QA Assistant",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Multi-Agent QA Assistant")
st.caption("Live API testing, response validation and report exports")

if "test_history" not in st.session_state:
    st.session_state.test_history = []


# Sidebar settings
st.sidebar.header("⚙️ API Test Settings")

default_url = "https://jsonplaceholder.typicode.com/users/1"

api_url = st.sidebar.text_input(
    "API Endpoint URL",
    value=default_url,
)

expected_status = st.sidebar.number_input(
    "Expected HTTP Status",
    min_value=100,
    max_value=599,
    value=200,
    step=1,
)

required_fields_text = st.sidebar.text_input(
    "Required JSON fields",
    value="id, name, email",
    help="Enter comma-separated top-level JSON fields.",
)

timeout = st.sidebar.number_input(
    "Timeout (seconds)",
    min_value=1,
    max_value=120,
    value=10,
)

required_fields = [
    field.strip()
    for field in required_fields_text.split(",")
    if field.strip()
]


# Run API test
st.subheader("🚀 Live API Tester")

if st.button("Run API Test", type="primary"):
    try:
        with st.spinner("Sending API request..."):
            result = run_live_api_test(
                api_url,
                expected_status=int(expected_status),
                required_fields=required_fields,
                timeout=timeout,
            )

        st.session_state.test_history.insert(0, result)
        st.session_state.test_history = (
            st.session_state.test_history[:100]
        )

    except (ValueError, TypeError) as error:
        st.error(f"Invalid test configuration: {error}")

    except Exception as error:
        st.error(f"Unexpected error: {error}")


# Current result and metrics
history = st.session_state.test_history

if history:
    latest = history[0]

    total_tests = len(history)
    passed_tests = sum(
        item.get("status") == "PASS" for item in history
    )
    failed_tests = total_tests - passed_tests

    st.subheader("📊 Test Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", total_tests)
    col2.metric("Passed", passed_tests)
    col3.metric("Failed", failed_tests)
    col4.metric(
        "Latest Response (ms)",
        latest.get("response_time_ms", "N/A"),
    )

    st.divider()

    st.subheader("🔎 Latest API Result")

    if latest.get("status") == "PASS":
        st.success("PASS — " + latest.get("message", ""))
    else:
        st.error("FAIL — " + latest.get("message", ""))

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.write("**Endpoint**")
        st.code(latest.get("url", ""))

        st.write("**HTTP Status Code**")
        st.write(latest.get("status_code", "N/A"))

    with result_col2:
        st.write("**Test ID**")
        st.write(latest.get("test_id", "N/A"))

        st.write("**Response Time**")
        st.write(
            f'{latest.get("response_time_ms", "N/A")} ms'
        )

    st.write("**JSON Response**")
    st.json(latest.get("json_data"))

    # Export latest result
    st.divider()
    st.subheader("📥 Download Reports")

    download_col1, download_col2, download_col3 = st.columns(3)

    with tempfile.TemporaryDirectory() as temp_dir:
        html_path = str(Path(temp_dir) / "live_api_report.html")
        csv_path = str(Path(temp_dir) / "live_api_report.csv")
        json_path = str(Path(temp_dir) / "live_api_report.json")

        export_live_api_html(latest, html_path)
        export_live_api_csv(latest, csv_path)
        export_live_api_json(latest, json_path)

        html_bytes = Path(html_path).read_bytes()
        csv_bytes = Path(csv_path).read_bytes()
        json_bytes = Path(json_path).read_bytes()

        with download_col1:
            st.download_button(
                "Download HTML",
                data=html_bytes,
                file_name="live_api_report.html",
                mime="text/html",
                key="download_html",
            )

        with download_col2:
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name="live_api_report.csv",
                mime="text/csv",
                key="download_csv",
            )

        with download_col3:
            st.download_button(
                "Download JSON",
                data=json_bytes,
                file_name="live_api_report.json",
                mime="application/json",
                key="download_json",
            )

    # Test history
    st.divider()
    st.subheader("📋 Test History")

    history_rows = []

    for item in history:
        history_rows.append({
            "Test ID": item.get("test_id", ""),
            "Status": item.get("status", ""),
            "HTTP Code": item.get("status_code", ""),
            "Response Time (ms)": item.get("response_time_ms", ""),
            "URL": item.get("url", ""),
            "Message": item.get("message", ""),
        })

    st.dataframe(
        history_rows,
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Clear Test History"):
        st.session_state.test_history = []
        st.rerun()

else:
    st.info(
        "No tests have been run in this session. "
        "Enter an API endpoint and click Run API Test."
    )

st.divider()
st.caption(
    "AI Multi-Agent QA Assistant | "
    "Python • API Testing • Automated Validation"
)
