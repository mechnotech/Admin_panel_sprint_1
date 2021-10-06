import os
import sqlite3
from typing import Optional

import psycopg2
from psycopg2._psycopg import AsIs
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, asdict


@dataclass
class Movie:

    __slots__ = (
        'id',
        'title',
        'description',
        'creation_date',
        'certificate',
        'file_path',
        'rating',
        'type',
        'created_at',
        'updated_at',
    )
    id: str
    title: str
    description: str
    creation_date: Optional[str]
    certificate: str
    file_path: str
    rating: float
    type: str
    created_at: str
    updated_at: str

    @property
    def get_keys(self):
        return ', '.join(self._get_cleaned_data.keys())

    @property
    def get_values(self):
        return list(map(lambda x: x, self._get_cleaned_data.values()))

    @property
    def get_len(self):
        return len(self._get_cleaned_data)

    @property
    def _get_cleaned_data(self):
        clean_data = {}
        for k, v in asdict(self).items():
            if not v:
                continue
            clean_data[k] = v
        return clean_data


def load_from_sqlite(sql_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    sql3_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    # c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # sql_tables = map(lambda item: item[0], c.fetchall())
    sql3_cursor.execute("SELECT * FROM film_work")

    while True:
        row = sql3_cursor.fetchone()
        if not row:
            break
        movie = Movie(*row)
        fields = movie.get_keys
        values = movie.get_values
        args = ', '.join(["%s"]*movie.get_len)
        #vl = pg_cursor.mogrify(args, values)
        # fields = 'id, title, description, rating, type, created_at, updated_at'
        # values =
        pg_cursor.execute(f"INSERT INTO film_work ({fields}) VALUES ({args}) ON CONFLICT (id) DO NOTHING;", values)
        #result = pg_cursor.fetchone()
        #print(result)

    # postgres_saver = PostgresSaver(pg_conn)
    # sqlite_loader = SQLiteLoader(connection)

    # data = sqlite_loader.load_movies()
    # postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': '172.16.238.10',
        'port': int(os.getenv('DB_PORT')),
        'options': '-c search_path=content'
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(
            **dsl,
            cursor_factory=DictCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
