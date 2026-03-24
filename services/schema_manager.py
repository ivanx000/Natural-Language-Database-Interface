from __future__ import annotations

"""Schema introspection helper used to ground SQL generation."""

import sqlite3
from dataclasses import dataclass


@dataclass
class SchemaManager:
    """Build a text schema snapshot from the SQLite catalog and pragmas."""

    db_path: str = "warehouse.db"

    def get_schema_context(self) -> str:
        """Return table, column, and foreign-key details for prompt context."""
        with sqlite3.connect(self.db_path) as conn:
            tables = self._get_tables(conn)
            sections: list[str] = []

            for table_name in tables:
                # PRAGMA table_info gives stable column ordering and metadata.
                column_rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                fk_rows = conn.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()

                col_lines = [
                    (
                        f"- {col[1]} {col[2]}"
                        f" {'NOT NULL' if col[3] else ''}"
                        f" {'PRIMARY KEY' if col[5] else ''}"
                    ).strip()
                    for col in column_rows
                ]

                fk_lines = [f"- {fk[3]} -> {fk[2]}.{fk[4]}" for fk in fk_rows]

                section = [f"Table: {table_name}", "Columns:"]
                section.extend(col_lines or ["- (none)"])
                section.append("Foreign Keys:")
                section.extend(fk_lines or ["- (none)"])
                sections.append("\n".join(section))

            return "\n\n".join(sections)

    @staticmethod
    def _get_tables(conn: sqlite3.Connection) -> list[str]:
        """Return user-defined table names in deterministic order."""
        rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        return [row[0] for row in rows]
