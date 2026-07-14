from sqlalchemy import text
from app.db.session import engine

def seed_business_tables():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            city TEXT NOT NULL
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            amount NUMERIC,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))

        count = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar_one()

        if count == 0:
            conn.execute(text("""
            INSERT INTO customers (name, level, city)
            VALUES
            ('Acme Ltd', 'VIP', 'Toronto'),
            ('Beta Inc', 'Normal', 'Vancouver')
            """))

            conn.execute(text("""
            INSERT INTO orders (customer_id, amount, status)
            VALUES
            (1, 1200, 'paid'),
            (1, 800, 'pending'),
            (2, 300, 'paid')
            """))