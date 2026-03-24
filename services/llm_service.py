from __future__ import annotations

"""LLM service for converting natural language questions into SQL.

The model is explicitly instructed to return raw SQL only. A post-processing
step enforces LIMIT protection on SELECT queries to keep result sets bounded.
"""

import os
import re

from openai import OpenAI
from sqlglot import parse_one

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DEFAULT_DIALECT = os.getenv("SQL_DIALECT", "sqlite")
DEFAULT_LIMIT = 10


def _extract_raw_sql(response_text: str) -> str:
    """Normalize model output into plain SQL text.

    The prompt is strict, but this fallback strips markdown fences in case the
    model still wraps the output.
    """
    text = response_text.strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _append_limit_if_needed(sql: str, default_limit: int = DEFAULT_LIMIT) -> str:
    """Append LIMIT to top-level SELECT statements that omit one."""
    stripped = sql.strip()
    if not re.match(r"^select\b", stripped, flags=re.IGNORECASE):
        return stripped

    try:
        expression = parse_one(stripped, read=DEFAULT_DIALECT)
        if expression.args.get("limit") is None:
            expression = expression.limit(default_limit)
        return expression.sql(dialect=DEFAULT_DIALECT)
    except Exception:
        # Fallback for SQL that cannot be parsed in the selected dialect.
        if re.search(r"\blimit\s+\d+\b", stripped, flags=re.IGNORECASE):
            return stripped
        if stripped.endswith(";"):
            return f"{stripped[:-1]} LIMIT {default_limit};"
        return f"{stripped} LIMIT {default_limit}"


def generate_sql(user_question: str, schema_context: str) -> str:
    """Generate SQL from natural language using schema-aware prompting."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = (
        "You are a senior SQL generation engine. "
        "Return ONLY a single raw SQL statement as plain text. "
        "Do not include markdown, backticks, comments, explanations, or extra prose. "
        "Use only tables and columns present in the provided schema context. "
        "If a column is not in schema context, do not invent it."
    )

    user_prompt = (
        "Schema context:\n"
        f"{schema_context}\n\n"
        "Question:\n"
        f"{user_question}\n\n"
        "Return exactly one valid SQL statement."
    )

    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    response_text = completion.choices[0].message.content or ""
    sql = _extract_raw_sql(response_text)
    return _append_limit_if_needed(sql)
