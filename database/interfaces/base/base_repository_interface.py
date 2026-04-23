import sqlite3


class IBaseRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Создание соединения с БД"""

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Для доступа по имени столбцов
        conn.execute("PRAGMA foreign_keys = ON")
        return conn