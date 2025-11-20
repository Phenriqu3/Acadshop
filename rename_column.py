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

    # Rename stripe_payment_intent_id to stripe_payment_id if it exists
    cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'orders' AND column_name = 'stripe_payment_intent_id') THEN
                ALTER TABLE orders RENAME COLUMN stripe_payment_intent_id TO stripe_payment_id;
                RAISE NOTICE 'Renamed stripe_payment_intent_id to stripe_payment_id';
            END IF;
        END $$;
    """)
    print("Renamed stripe_payment_intent_id to stripe_payment_id if it existed")

    conn.commit()
    print("Column rename complete")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
