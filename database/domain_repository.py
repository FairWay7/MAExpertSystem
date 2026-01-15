import sqlite3
import uuid
from typing import Optional, Dict, List


class DomainRepository:
    """CRUD операции для доменов"""

    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Создание соединения с БД"""

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Для доступа по имени столбцов
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_domain(self, name: str, description: str = "") -> Optional[Dict]:
        """Создание новой предметной области"""
        domain_id = str(uuid.uuid4())

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO domains (id, name, description)
                VALUES (?, ?, ?)
                ''', (domain_id, name, description))

            conn.commit()
            conn.close()

            return self.get_domain(domain_id)

        except sqlite3.Error as e:
            print(f"Ошибка создания домена: {e}")
            return None

    def get_domain(self, domain_id: str) -> Optional[Dict]:
        """Получение домена по ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM domains WHERE id = ?', (domain_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Ошибка получения домена: {e}")
            return None

    def get_domain_by_name(self, name: str) -> Optional[Dict]:
        """Получение домена по имени"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM domains WHERE name = ?', (name,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Ошибка получения домена: {e}")
            return None

    def get_all_domains(self) -> List[Dict]:
        """Получение всех доменов"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM domains ORDER BY name')
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения доменов: {e}")
            return []