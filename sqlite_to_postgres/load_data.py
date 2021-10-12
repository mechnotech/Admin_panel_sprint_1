import io
import logging
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

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

    def __del__(self):
        self.cursor.close()


class PostgresSaver(SQLiteLoader):

    def save_all_data(self, data):
        counter = 0

        for block in data:
            block_values = '\n'.join([obj.get_values for obj in block])
            with io.StringIO(block_values) as f:
                self.cursor.copy_from(f, table=self.table_name, null='None', size=BLOCK_SIZE)
            counter += 1

        if self.verbose:
            log.info('В таблицу %s вставлено: %s блоков', self.table_name, counter)


def load_from_sqlite(sql_conn: sqlite3.Connection, psg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    for table_name, data_class in TABLES_TO_CLASSES.items():
        try:
            sqlite_loader = SQLiteLoader(sql_conn, table_name, data_class, verbose=True)
            data = sqlite_loader.load_table()
        except Exception:
            log.exception('При чтении из SQLite произошла ошибка')
            break
        try:
            postgres_saver = PostgresSaver(psg_conn, table_name, data_class, verbose=True)
            postgres_saver.save_all_data(data)
        except Exception:
            log.exception('При записи в Postgres произошла ошибка')
            break


if __name__ == '__main__':
    dsl = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('DB_DEV_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'options': '-c search_path=content'
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)

    sqlite_conn.close()
    pg_conn.close()
