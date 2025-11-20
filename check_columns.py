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

    # Check columns in orders table
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'orders'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()
    print("Columns in orders table:")
    for col in columns:
        print(f"- {col[0]}")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
