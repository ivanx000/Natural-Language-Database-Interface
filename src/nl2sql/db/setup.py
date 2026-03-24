from __future__ import annotations

"""Database setup orchestration for schema creation and seeding."""

from typing import Optional

from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .models import Base, Customer, Order, Product
from .seed_data import build_customers, build_orders, build_products


def create_sqlite_engine(database_url: str = "sqlite:///warehouse.db") -> Engine:
    """Create an engine and enforce foreign key checks for SQLite."""
    engine = create_engine(database_url, future=True)

    if database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            del connection_record
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_schema(engine: Engine) -> None:
    """Create all database tables."""
    Base.metadata.create_all(engine)


def seed_database(session: Session) -> None:
    """Seed customers/products/orders when database is empty."""
    has_customers = session.scalar(select(Customer.id).limit(1)) is not None
    has_products = session.scalar(select(Product.id).limit(1)) is not None
    has_orders = session.scalar(select(Order.id).limit(1)) is not None

    if has_customers or has_products or has_orders:
        return

    customers = build_customers()
    products = build_products()

    session.add_all(customers)
    session.add_all(products)
    session.flush()

    orders = build_orders(customers=customers, products=products)
    session.add_all(orders)
    session.commit()


def initialize_database(database_url: Optional[str] = None) -> None:
    """Create schema and seed baseline data for local development."""
    db_url = database_url or "sqlite:///warehouse.db"
    engine = create_sqlite_engine(db_url)

    create_schema(engine)

    with Session(engine) as session:
        seed_database(session)
