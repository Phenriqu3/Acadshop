import psycopg2
from psycopg2 import sql
import os
import subprocess

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = 'postgres'
DB_PASSWORD = '290703'
DB_NAME = 'acadshop_db'

def execute_sql_file(cursor, file_path):
    """Execute SQL file with proper statement parsing"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    statements = []
    current_statement = ''
    in_multiline_comment = False

    for line in content.split('\n'):
        stripped_line = line.strip()

        if stripped_line.startswith('/*'):
            in_multiline_comment = True
            continue
        if '*/' in stripped_line:
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        if stripped_line.startswith('--') or not stripped_line:
            continue

        current_statement += line + '\n'

        if stripped_line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ''

    if current_statement.strip():
        statements.append(current_statement.strip())

    for statement in statements:
        if not statement.strip():
            continue
        try:
            cursor.execute(statement)
            cursor.connection.commit()
            print(f"Executed: {statement.strip()[:60]}...")
        except Exception as e:
            print(f"Error executing statement: {e}")
            print(f"Statement was: {statement[:100]}...")
            cursor.connection.rollback()

def run_flask_setup():
    """Run Flask database initialization"""
    try:
        print("Executando inicialização do banco de dados Flask...")
        subprocess.run(['python', '-c', '''
from app import app, db
with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")
        '''], check=True)
        print("Inicialização do Flask executada com sucesso.")

        print("Executando seed do banco de dados...")
        subprocess.run(['python', 'seed.py'], check=True)
        print("Seed executado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar inicialização Flask: {e}")
        return False

def show_database_info(cursor):
    """Show some basic database information"""
    try:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("\n=== Tabelas criadas ===")
        for table in tables:
            print(f"- {table[0]}")

        print("\n=== Contagem de registros ===")
        for table_name, in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"{table_name}: {count} registros")
            except:
                print(f"{table_name}: erro ao contar")

    except Exception as e:
        print(f"Erro ao mostrar informações do banco: {e}")

def main(): 
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Terminate active connections to the database
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid();
        """, (DB_NAME,))
        print(f"Conexões ativas ao banco de dados {DB_NAME} terminadas.")

        # Drop the database if it exists
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
        print(f"Banco de dados {DB_NAME} removido se existia.")

        # Create the database
        cursor.execute(sql.SQL("CREATE DATABASE {} WITH ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE template0").format(sql.Identifier(DB_NAME)))
        print(f"Banco de dados {DB_NAME} criado.")

        cursor.close()
        conn.close()

        # Now connect to the new database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Execute the SQL setup file
        sql_file = 'acadshop_full_setup.sql'
        if os.path.exists(sql_file):
            print(f"Executando arquivo SQL: {sql_file}")
            execute_sql_file(cursor, sql_file)
        else:
            print(f"Arquivo {sql_file} não encontrado. Pulando execução de SQL.")

        # Run Flask database setup
        flask_success = run_flask_setup()

        if flask_success:
            # Show database information
            show_database_info(cursor)
        else:
            print("Inicialização Flask falhou. Verifique os logs acima.")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n=== Configuração concluída ===")
        print("Banco de dados criado e configurado com sucesso!")
        print("Você pode agora executar 'python app.py' para iniciar o servidor Flask.")

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
