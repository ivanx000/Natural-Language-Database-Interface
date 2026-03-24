from __future__ import annotations

"""Streamlit dashboard for the NL2SQL experience."""

from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from services.db_executor import SecurityError, execute_query
from services.llm_service import generate_sql
from services.schema_manager import SchemaManager


def _looks_like_datetime(series: pd.Series) -> bool:
    """Heuristically detect date-like columns for chart-friendly rendering."""
    if series.empty:
        return False
    converted = pd.to_datetime(series, errors="coerce")
    valid_ratio = converted.notna().mean()
    return bool(valid_ratio >= 0.7)


def _prepare_chart_data(df: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    """Prepare line/bar chart data when result shape is visualization-friendly."""
    if df.empty or len(df.columns) < 2:
        return None, None

    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        return None, None

    date_col = None
    for col in df.columns:
        if _looks_like_datetime(df[col]):
            date_col = col
            break

    if date_col is not None:
        chart_df = df[[date_col, numeric_cols[0]]].copy()
        chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[date_col]).sort_values(by=date_col)
        if chart_df.empty:
            return None, None
        chart_df = chart_df.set_index(date_col)
        return chart_df, "line"

    first_col = df.columns[0]
    chart_df = df[[first_col, numeric_cols[0]]].copy()
    chart_df[first_col] = chart_df[first_col].astype(str)
    chart_df = chart_df.groupby(first_col, as_index=True)[numeric_cols[0]].sum().sort_values(ascending=False)
    chart_df = chart_df.head(20).to_frame()
    if chart_df.empty:
        return None, None
    return chart_df, "bar"


def _render_result_payload(payload: list[dict[str, Any]] | dict[str, str]) -> None:
    """Render query output and optional chart preview to the Streamlit UI."""
    if isinstance(payload, dict) and "error" in payload:
        st.error(payload["error"])
        return

    rows = payload
    if not rows:
        st.info("No rows returned.")
        return

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    chart_df, chart_kind = _prepare_chart_data(df)
    if chart_df is None or chart_kind is None:
        return

    st.caption("Auto chart preview")
    if chart_kind == "line":
        st.line_chart(chart_df, use_container_width=True)
    else:
        st.bar_chart(chart_df, use_container_width=True)


def _run_query_flow(question: str, schema_context: str) -> tuple[str, list[dict[str, Any]] | dict[str, str]]:
    """Generate SQL and execute it with security-aware error handling."""
    sql_query = generate_sql(user_question=question, schema_context=schema_context)

    try:
        result = execute_query(sql_query)
    except SecurityError as exc:
        return sql_query, {"error": f"Security error: {exc}"}

    return sql_query, result


def main() -> None:
    """Launch the Streamlit chat workflow for NL2SQL queries."""
    load_dotenv()

    st.set_page_config(page_title="NL2SQL Dashboard", page_icon="DB", layout="wide")
    st.title("NL2SQL Dashboard")
    st.write("Ask a question in plain English and explore the generated SQL and results.")

    if "history" not in st.session_state:
        st.session_state.history = []

    # Cache schema context for the run so repeated prompts stay consistent.
    schema_context = SchemaManager().get_schema_context()

    for item in st.session_state.history:
        with st.chat_message("user"):
            st.write(item["question"])

        with st.chat_message("assistant"):
            with st.expander("Expert Mode: Generated SQL", expanded=False):
                st.code(item["sql"], language="sql")
            _render_result_payload(item["result"])

    prompt = st.chat_input("Ask a question about your warehouse data")
    if not prompt:
        return

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL and fetching results..."):
            sql_query, result = _run_query_flow(question=prompt, schema_context=schema_context)

        with st.expander("Expert Mode: Generated SQL", expanded=False):
            st.code(sql_query, language="sql")

        _render_result_payload(result)

    st.session_state.history.append(
        {
            "question": prompt,
            "sql": sql_query,
            "result": result,
        }
    )


if __name__ == "__main__":
    main()
