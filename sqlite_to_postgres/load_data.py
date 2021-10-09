import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from data_classes import Movie, Person, Genre, GenreFilmWork, PersonFilmWork

load_dotenv()


class SQLiteLoader:
    def __init__(self, connection, verbose=False):
        self.connection = connection
        self.data_container = []
        self.cursor = self.connection.cursor()
        self.verbose = verbose

    def load_table(self, table_name: str):
        data_class = TABLES_TO_CLASSES[table_name]
        self.data_container.clear()
        self.cursor.execute(f'SELECT * FROM {table_name}')

        while True:
            block_rows = self.cursor.fetchmany(size=BLOCK_SIZE)
            if not block_rows:
                break
            block = []
            for row in block_rows:
                data = data_class(*row)
                block.append(data)
            self.data_container.append(block)

        if self.verbose:
            print(f'Загружено: из {table_name} {len(self.data_container)} блоков')

        return {'table_name': table_name, 'data': self.data_container}


class PostgresSaver(SQLiteLoader):

    def load_table(self, table_name):
        raise NotImplementedError("function load_table not implemented")

    def save_all_data(self, data: dict):
        table_name = data['table_name']
        data = data['data']
        block_args = []
        block_values = []

        for block in data:
            block_args.clear()
            block_values.clear()
            for obj in block:
                fields = obj.get_fields
                values = obj.get_values
                row_args = '(' + ', '.join(["%s"] * obj.get_len) + ')'
                block_args.append(row_args)
                block_values += values
            args = ', '.join(block_args)
            query = f'INSERT INTO {table_name} ({fields}) VALUES {args} ON CONFLICT (id) DO NOTHING;'
            self.cursor.execute(query, block_values)

        if self.verbose:
            print(f'В таблицу {table_name} вставлено: {len(data)} блоков')


def load_from_sqlite(sql_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_loader = SQLiteLoader(sql_conn, verbose=True)
    postgres_saver = PostgresSaver(pg_conn, verbose=True)
    for key in TABLES_TO_CLASSES.keys():
        try:
            data = sqlite_loader.load_table(key)
        except Exception as e:
            print(f'При чтении из SQLite произошла ошибка {e}')
            break
        try:
            postgres_saver.save_all_data(data)
        except Exception as e:
            print(f'При записи в Postgres произошла ошибка {e}')
            break


if __name__ == '__main__':
    BLOCK_SIZE = 10
    TABLES_TO_CLASSES = {
        'film_work': Movie,
        'genre': Genre,
        'person': Person,
        'genre_film_work': GenreFilmWork,
        'person_film_work': PersonFilmWork

    }
    dsl = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': '172.16.238.10',
        'port': int(os.getenv('DB_PORT')),
        'options': '-c search_path=content'
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
