
import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from live_api_tester import run_live_api_test


st.set_page_config(
    page_title="AI Multi-Agent QA Assistant",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Multi-Agent QA Assistant")
st.caption("Live API Testing Dashboard")

# Keep test history during the current session.
if "api_test_history" not in st.session_state:
    st.session_state.api_test_history = []


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


st.subheader("Run a Live API Test")

url = st.text_input(
    "API endpoint URL",
    value="https://jsonplaceholder.typicode.com/users/1",
    help="Enter a valid HTTP or HTTPS API endpoint.",
)

required_fields_text = st.text_input(
    "Required JSON fields (comma-separated)",
    value="id,name,email",
)

if st.button("🚀 Run API Test", type="primary"):
    required_fields = [
        field.strip()
        for field in required_fields_text.split(",")
        if field.strip()
    ]

    try:
        with st.spinner("Testing API endpoint..."):
            result = run_live_api_test(
                url,
                expected_status=int(expected_status),
                required_fields=required_fields,
                timeout=float(timeout),
            )

        if not isinstance(result, dict):
            raise TypeError(
                "run_live_api_test must return a dictionary."
            )

        result.setdefault("test_id", f"API_{len(st.session_state.api_test_history) + 1:03d}")
        result.setdefault("url", url)
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

    except (TypeError, ValueError) as exc:
        st.error(f"Invalid input or test result: {exc}")
    except Exception as exc:
        st.error(f"Unable to run API test: {exc}")


st.divider()
st.subheader("📊 Test Summary")

history = st.session_state.api_test_history

if history:
    total = len(history)
    passed = sum(item.get("status") == "PASS" for item in history)
    failed = total - passed

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tests", total)
    col2.metric("Passed", passed)
    col3.metric("Failed", failed)

    st.subheader("Test History")
    df = pd.DataFrame(history)
    st.dataframe(df, use_container_width=True)

    # Export reports directly from the dashboard.
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    json_data = json.dumps(
        history,
        indent=2,
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")

    html_rows = []
    for item in history:
        test_id = str(item.get("test_id", ""))
        status = str(item.get("status", ""))
        message = str(item.get("message", ""))

        # Escape content before placing it in HTML.
        import html

        html_rows.append(
            "<tr>"
            f"<td>{html.escape(test_id)}</td>"
            f"<td>{html.escape(status)}</td>"
            f"<td>{html.escape(message)}</td>"
            "</tr>"
        )

    html_data = f"""<!DOCTYPE html>
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
<p>Total: {total} | Passed: {passed} | Failed: {failed}</p>
<table>
<thead><tr><th>Test ID</th><th>Status</th><th>Message</th></tr></thead>
<tbody>{"".join(html_rows)}</tbody>
</table>
</body>
</html>
""".encode("utf-8")

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
