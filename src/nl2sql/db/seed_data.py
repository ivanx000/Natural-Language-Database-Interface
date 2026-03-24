from __future__ import annotations

"""Seed-data factories used during local database bootstrap."""

from datetime import datetime, timedelta

from .models import Customer, Order, Product


def build_customers() -> list[Customer]:
    """Return realistic customer seed data."""
    return [
        Customer(first_name="Ava", last_name="Johnson", email="ava.johnson@example.com", city="Seattle"),
        Customer(first_name="Liam", last_name="Patel", email="liam.patel@example.com", city="Austin"),
        Customer(first_name="Mia", last_name="Garcia", email="mia.garcia@example.com", city="Chicago"),
        Customer(first_name="Noah", last_name="Kim", email="noah.kim@example.com", city="San Diego"),
        Customer(first_name="Emma", last_name="Smith", email="emma.smith@example.com", city="Boston"),
        Customer(first_name="Lucas", last_name="Brown", email="lucas.brown@example.com", city="Denver"),
        Customer(first_name="Sophia", last_name="Davis", email="sophia.davis@example.com", city="Phoenix"),
        Customer(first_name="Ethan", last_name="Wilson", email="ethan.wilson@example.com", city="Portland"),
        Customer(first_name="Olivia", last_name="Martinez", email="olivia.martinez@example.com", city="Miami"),
        Customer(first_name="James", last_name="Nguyen", email="james.nguyen@example.com", city="New York"),
    ]


def build_products() -> list[Product]:
    """Return product catalog seed data."""
    return [
        Product(sku="ELEC-001", name="Wireless Keyboard", category="Electronics", price=49.99, stock=120),
        Product(sku="ELEC-002", name="Bluetooth Mouse", category="Electronics", price=29.99, stock=200),
        Product(sku="ELEC-003", name="USB-C Hub", category="Electronics", price=59.99, stock=80),
        Product(sku="HOME-001", name="Ceramic Mug Set", category="Home", price=24.99, stock=150),
        Product(sku="HOME-002", name="Desk Lamp", category="Home", price=39.99, stock=95),
        Product(sku="OFFC-001", name="Ergonomic Chair", category="Office", price=199.99, stock=35),
        Product(sku="OFFC-002", name="Standing Desk", category="Office", price=399.99, stock=20),
        Product(sku="SPRT-001", name="Yoga Mat", category="Sports", price=34.99, stock=110),
        Product(sku="SPRT-002", name="Resistance Bands", category="Sports", price=19.99, stock=180),
        Product(sku="BOOK-001", name="Data Engineering Handbook", category="Books", price=44.99, stock=60),
    ]


def build_orders(customers: list[Customer], products: list[Product]) -> list[Order]:
    """Return order seed data linked to existing customers/products."""
    statuses = ["processing", "shipped", "delivered", "cancelled"]
    now = datetime.utcnow()

    order_specs = [
        (0, 0, 1, statuses[2], 2),
        (1, 1, 2, statuses[1], 3),
        (2, 2, 1, statuses[2], 5),
        (3, 3, 1, statuses[0], 1),
        (4, 4, 3, statuses[2], 7),
        (5, 5, 1, statuses[1], 4),
        (6, 6, 2, statuses[2], 9),
        (7, 7, 1, statuses[0], 6),
        (8, 8, 4, statuses[1], 8),
        (9, 9, 1, statuses[2], 10),
        (0, 3, 1, statuses[2], 11),
        (1, 5, 1, statuses[0], 12),
    ]

    orders: list[Order] = []
    for customer_idx, product_idx, qty, status, days_ago in order_specs:
        product = products[product_idx]
        orders.append(
            Order(
                customer=customers[customer_idx],
                product=product,
                quantity=qty,
                unit_price=product.price,
                status=status,
                order_date=now - timedelta(days=days_ago),
            )
        )

    return orders
