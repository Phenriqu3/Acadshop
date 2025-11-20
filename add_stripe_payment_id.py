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

    # Add stripe_payment_id column if it doesn't exist
    cursor.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS stripe_payment_id VARCHAR(100)
    """)
    print("Added stripe_payment_id column")

    conn.commit()
    print("Database update complete")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
