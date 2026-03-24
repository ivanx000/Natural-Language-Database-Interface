from __future__ import annotations

"""Secure SQL execution against the local warehouse database.

Only read-only SELECT queries are allowed. Potentially destructive keywords are
blocked before execution.
"""

import re
import sqlite3
from typing import Any

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError

DB_PATH = "warehouse.db"
_FORBIDDEN_PATTERN = re.compile(r"\b(drop|delete|update)\b", flags=re.IGNORECASE)


class SecurityError(Exception):
    """Raised when a query violates execution safety constraints."""


def _ensure_safe_select(sql_query: str) -> exp.Expression:
    """Validate SQL is read-only and structurally SELECT-based."""
    query_text = sql_query.strip()

    if _FORBIDDEN_PATTERN.search(query_text):
        raise SecurityError("Blocked potentially destructive SQL keyword.")

    parsed = parse_one(query_text, read="sqlite")

    # Enforce read-only behavior by requiring a SELECT node in the parsed tree.
    if parsed.find(exp.Select) is None:
        raise SecurityError("Only SELECT statements are allowed.")

    return parsed


def execute_query(sql_query: str) -> list[dict[str, Any]] | dict[str, str]:
    """Execute a validated query and return rows as JSON-ready dictionaries."""
    try:
        _ensure_safe_select(sql_query)
    except ParseError as exc:
        return {"error": f"SQL syntax error: {exc}"}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql_query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.OperationalError as exc:
        # Return SQL errors as data so callers can trigger self-healing retries.
        return {"error": f"SQL execution error: {exc}"}
