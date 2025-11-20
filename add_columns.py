import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Add payment_status column if it doesn't exist
try:
    cursor.execute("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pending'")
    print("Added payment_status column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("payment_status column already exists")
    else:
        print(f"Error adding payment_status: {e}")

# Add stripe_payment_method_id column if it doesn't exist
try:
    cursor.execute("ALTER TABLE orders ADD COLUMN stripe_payment_method_id VARCHAR(100)")
    print("Added stripe_payment_method_id column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("stripe_payment_method_id column already exists")
    else:
        print(f"Error adding stripe_payment_method_id: {e}")

# Commit changes and close
conn.commit()
conn.close()
print("Database update complete")
