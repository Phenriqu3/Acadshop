import psycopg2
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Verifica a conexão com o banco de dados PostgreSQL'

    def handle(self, *args, **options):
        try:
            conn = psycopg2.connect(
                dbname='acadshop_db',
                user='postgres',
                password='290703',
                host='localhost',
                port='5432'
            )
            conn.close()
            self.stdout.write(self.style.SUCCESS('Conectado com sucesso ao banco de dados PostgreSQL!'))
        except psycopg2.OperationalError as e:
            self.stdout.write(self.style.ERROR(f'Erro operacional no banco de dados (verifique se o PostgreSQL está rodando e as credenciais estão corretas): {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro desconhecido na conexão: {e}'))
