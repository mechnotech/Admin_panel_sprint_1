import logging
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values

from data_classes import Movie, Person, Genre, GenreFilmWork, PersonFilmWork

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

BLOCK_SIZE = 100
TABLES_TO_CLASSES = {
    'film_work': Movie,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork,
}


class SQLiteLoader:
    def __init__(self, connection, table_name, data_class, verbose=False):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.verbose = verbose
        self.table_name = table_name
        self.data_class = data_class
        self.cursor.execute(f'SELECT * FROM {self.table_name}')

    def load_table(self):

        counter = 0
        while True:
            block_rows = self.cursor.fetchmany(size=BLOCK_SIZE)
            if not block_rows:
                break
            block = []
            for row in block_rows:
                data = self.data_class(*row)
                block.append(data)
            yield block
            counter += 1

        if self.verbose:
            log.info('Загружено: из %s %s блоков', self.table_name, counter)


class PostgresSaver(SQLiteLoader):

    def save_all_data(self, data):
        block_values = []
        counter = 0
        
        for block in data:
            block_values.clear()

            for obj in block:
                values = tuple(obj.get_values)
                block_values.append(values)
            query = f'INSERT INTO {self.table_name} VALUES %s ON CONFLICT (id) DO NOTHING;'
            execute_values(self.cursor, query, block_values)
            counter += 1

        if self.verbose:
            log.info('В таблицу %s вставлено: %s блоков', self.table_name, counter)


def load_from_sqlite(sql_conn: sqlite3.Connection, psg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    for key, value in TABLES_TO_CLASSES.items():
        try:
            sqlite_loader = SQLiteLoader(sql_conn, table_name=key, data_class=value, verbose=True)
            data = sqlite_loader.load_table()
        except Exception as e:
            log.critical(f'При чтении из SQLite произошла ошибка {e}')
            break
        try:
            postgres_saver = PostgresSaver(psg_conn, table_name=key, data_class=value, verbose=True)
            postgres_saver.save_all_data(data)
        except Exception as e:
            log.critical(f'При записи в Postgres произошла ошибка {e}')
            break


if __name__ == '__main__':
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

    sqlite_conn.close()
    pg_conn.close()
