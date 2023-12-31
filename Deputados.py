import requests
import psycopg2
from psycopg2 import sql

# Fazendo a requisição

url = 'https://dadosabertos.camara.leg.br/api/v2/deputados'

params = {'idLegislatura': '56', 'ordenarPor': 'id'}

# params = {'dataInicio':'2020-01-01','dataFim':'2020-12-31'}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Erro ao fazer a requisição: {e}")
    exit()

data = response.json()

# Conectando ao banco de dados
try:
    with psycopg2.connect(
        dbname="pi2",
        user="postgres",
        password="2605",
        host="localhost",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            # Criando a tabela
            table_create_query = """
            CREATE TABLE IF NOT EXISTS deputados (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255),
                partido VARCHAR(50) REFERENCES partidos(sigla)
            )
            """
            cur.execute(table_create_query)

            # Inserindo os dados na tabela
            for deputado in data['dados']:
                insert_query = sql.SQL("""
                    INSERT INTO deputados (id, nome, partido) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """)
                cur.execute(
                    insert_query, (deputado['id'], deputado['nome'], deputado['siglaPartido']))

            conn.commit()
except psycopg2.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
