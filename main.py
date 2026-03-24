from __future__ import annotations

"""CLI entrypoint for the NL2SQL workflow.

This mode is useful for debugging and quick verification without launching the
Streamlit dashboard.
"""

from typing import Any

from dotenv import load_dotenv

from services.db_executor import SecurityError, execute_query
from services.llm_service import generate_sql
from services.schema_manager import SchemaManager


def _format_table(rows: list[dict[str, Any]]) -> str:
    """Render rows as a readable plain-text table."""
    if not rows:
        return "No rows returned."

    headers = list(rows[0].keys())
    table_rows = [[str(row.get(header, "")) for header in headers] for row in rows]

    widths = [len(header) for header in headers]
    for row in table_rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    header_line = " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers))
    divider_line = "-+-".join("-" * widths[idx] for idx in range(len(headers)))
    value_lines = [
        " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))
        for row in table_rows
    ]

    return "\n".join([header_line, divider_line, *value_lines])


def main() -> None:
    """Run the terminal-based NL2SQL workflow."""
    load_dotenv()

    user_question = input("Ask your data question: ").strip()
    if not user_question:
        print("Question cannot be empty.")
        return

    # Build prompt context from the live database schema.
    schema_context = SchemaManager().get_schema_context()
    sql_query = generate_sql(user_question=user_question, schema_context=schema_context)

    print("\nGenerated SQL:")
    print(sql_query)

    try:
        result = execute_query(sql_query)
    except SecurityError as exc:
        print(f"\nSecurity error: {exc}")
        return

    if isinstance(result, dict) and "error" in result:
        print(f"\nQuery error: {result['error']}")
        return

    print("\nResults:")
    print(_format_table(result))


if __name__ == "__main__":
    main()
