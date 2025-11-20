#!/usr/bin/env python3
"""
Simple PostgreSQL Database Shell for AcadShop
Use this as an alternative to psql command line tool
"""

import psycopg2
import sys
import os

def get_connection():
    """Get database connection"""
    try:
        return psycopg2.connect(
            host="localhost",
            database="acadshop_db",
            user="postgres",
            password="290703"
        )
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def execute_query(query, fetch=True):
    """Execute a SQL query"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(query)
        if fetch and cur.description:
            results = cur.fetchall()
            # Print column headers
            if cur.description:
                headers = [desc[0] for desc in cur.description]
                print(" | ".join(headers))
                print("-" * (sum(len(h) for h in headers) + len(headers) * 3 - 1))
                # Print rows
                for row in results:
                    print(" | ".join(str(cell) for cell in row))
            print(f"\n{len(results)} rows returned")
        else:
            print("Query executed successfully")
            if 'INSERT' in query.upper() or 'UPDATE' in query.upper() or 'DELETE' in query.upper():
                print(f"Rows affected: {cur.rowcount}")

        conn.commit()

    except Exception as e:
        print(f"❌ Query failed: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def show_help():
    """Show available commands"""
    print("""
=== AcadShop Database Shell ===

Available commands:
  .help          - Show this help
  .tables        - List all tables
  .users         - Show users
  .products      - Show products
  .categories    - Show categories
  .reviews       - Show site reviews
  .exit          - Exit the shell

Or enter any SQL query directly.

Examples:
  SELECT * FROM "user" LIMIT 5;
  SELECT COUNT(*) FROM product;
  SELECT name, price FROM product WHERE price > 100;
""")

def main():
    print("=== AcadShop Database Shell ===")
    print("Type '.help' for commands or enter SQL queries")
    print("Type '.exit' to quit\n")

    while True:
        try:
            query = input("db> ").strip()

            if not query:
                continue

            if query.lower() in ['.exit', 'exit', 'quit', 'q']:
                print("Goodbye!")
                break

            elif query.lower() == '.help':
                show_help()

            elif query.lower() == '.tables':
                execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")

            elif query.lower() == '.users':
                execute_query('SELECT id, username, email, is_admin, created_at FROM "user";')

            elif query.lower() == '.products':
                execute_query('SELECT id, name, price, stock, category_id FROM product ORDER BY created_at DESC;')

            elif query.lower() == '.categories':
                execute_query('SELECT id, name, slug, product_count FROM category;')

            elif query.lower() == '.reviews':
                execute_query('SELECT id, name, rating, comment FROM site_review WHERE is_approved = true;')

            else:
                # Execute as SQL query
                execute_query(query)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
