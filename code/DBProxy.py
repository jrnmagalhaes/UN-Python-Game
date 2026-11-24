import sqlite3
from datetime import datetime

from code.Const import DB_DATE_FORMAT, SCORE_TOP


class DBProxy:

    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                time_ms INTEGER NOT NULL,
                date    TEXT    NOT NULL
            )
        ''')
        self.connection.commit()

    def save(self, name: str, time_ms: int, date: datetime = None) -> int:
        date = date or datetime.now()
        cursor = self.connection.execute('INSERT INTO runs (name, time_ms, date) VALUES (?, ?, ?)',
                                         (name, int(time_ms), date.strftime(DB_DATE_FORMAT)))
        self.connection.commit()
        return cursor.lastrowid

    def top10(self) -> list:
        cursor = self.connection.execute('SELECT id, name, time_ms, date FROM runs '
                                         'ORDER BY time_ms ASC, id ASC LIMIT ?', (SCORE_TOP,))
        return cursor.fetchall()

    def close(self):
        self.connection.close()
