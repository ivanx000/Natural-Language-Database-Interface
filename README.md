# Natural Language Database Interface

A production-style NL2SQL demo that converts plain-English questions into SQL,
enforces read-only execution rules, and visualizes results in a Streamlit
dashboard.

## Features

- Natural language to SQL generation using OpenAI (default model: gpt-4o)
- Schema-aware prompting to avoid invalid table/column references
- SQL safety checks that block destructive operations
- Automatic LIMIT protection for SELECT queries
- Chat-style Streamlit UI with SQL transparency (Expert Mode)
- Optional CLI flow for fast debugging

## Tech Stack

- Python 3.10+
- SQLite (local development database)
- SQLAlchemy (schema and seeding)
- sqlglot (SQL parsing and safety checks)
- OpenAI SDK (LLM integration)
- Streamlit + pandas (dashboard and visualization)

## Project Layout

- `app.py`: Streamlit dashboard entrypoint
- `main.py`: CLI entrypoint
- `setup_db.py`: Creates and seeds the local database
- `services/llm_service.py`: LLM SQL generation and post-processing
- `services/db_executor.py`: Query validation and execution
- `services/schema_manager.py`: Runtime schema introspection
- `src/nl2sql/db/models.py`: SQLAlchemy models
- `src/nl2sql/db/seed_data.py`: Customer/product/order sample data
- `src/nl2sql/db/setup.py`: Schema creation and seeding orchestration
- `.env.example`: Environment variable template

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
3. Configure environment:
   - `cp .env.example .env`
   - Add your OpenAI API key to `OPENAI_API_KEY`
4. Initialize the database:
   - `python setup_db.py`

## Run the App

- Streamlit dashboard:
  - `streamlit run app.py`
- CLI mode:
  - `python main.py`

## Example Questions

- Show the top 10 customers by number of orders.
- List products with the highest total quantity sold.
- Show daily order counts.
- Show total sales by product category.

## Security and Execution Rules

- Only SELECT-style queries are executed.
- Queries containing DROP, DELETE, or UPDATE are blocked.
- If generated SELECT SQL has no LIMIT, LIMIT 10 is appended.

## Data Model

- `customers`: profile information for buyers
- `products`: catalog and inventory fields
- `orders`: fact table with foreign keys to customers and products

The seed script creates realistic sample rows for all three tables.

## GitHub Publishing Notes

- `.env`, local virtual environments, caches, and local database files are
  ignored by `.gitignore`.
- `warehouse.db` is generated locally and should not be committed.
- If needed, regenerate local data anytime with:
  - `python setup_db.py`
