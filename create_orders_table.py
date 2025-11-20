import psycopg2

# Database connection parameters
conn_params = {
    'host': 'localhost',
    'database': 'acadshop_db',
    'user': 'postgres',
    'password': '290703'
}

try:
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            total_amount NUMERIC(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            payment_method VARCHAR(50),
            payment_status VARCHAR(20) DEFAULT 'pending',
            stripe_payment_id VARCHAR(100),
            stripe_payment_method_id VARCHAR(100),
            shipping_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created orders table")

    # Create order_items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            size VARCHAR(20),
            color VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created order_items table")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id)")
    print("Created indexes")

    conn.commit()
    print("Database update complete")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
