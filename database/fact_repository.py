import sqlite3
import uuid
from typing import Dict, Optional, List


class FactRepository:
    """CRUD операции для фактов"""

    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Создание соединения с БД"""

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Для доступа по имени столбцов
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def save_fact(self, fact_data: Dict) -> Optional[Dict]:
        """Сохранение факта"""
        # Проверяем обязательные поля
        required = ['variable_name', 'value', 'agent_id']
        for field in required:
            if field not in fact_data:
                print(f"Ошибка: отсутствует обязательное поле '{field}'")
                return None

        # Генерируем ID если нет
        if 'id' not in fact_data:
            fact_data['id'] = str(uuid.uuid4())

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO facts (
                    id, variable_name, value, confidence,
                    source_file, author, is_derived, agent_id, domain_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                fact_data['id'],
                fact_data['variable_name'],
                str(fact_data['value']),
                fact_data.get('confidence', 1.0),
                fact_data.get('source_file', ''),
                fact_data.get('author', 'system'),
                1 if fact_data.get('is_derived', False) else 0,
                fact_data['agent_id'],
                fact_data.get('domain_id')
            ))

            # Обновляем счетчик фактов в домене
            if fact_data.get('domain_id'):
                cursor.execute('''
                    UPDATE domains 
                    SET facts_count = facts_count + 1 
                    WHERE id = ?
                    ''', (fact_data['domain_id'],))

            conn.commit()
            conn.close()

            return self.get_fact(fact_data['id'])

        except sqlite3.Error as e:
            print(f"Ошибка сохранения факта: {e}")
            return None

    def get_fact(self, fact_id: str) -> Optional[Dict]:
        """Получение факта по ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM facts WHERE id = ?', (fact_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Ошибка получения факта: {e}")
            return None

    def get_facts_by_agent(self, agent_id: str) -> List[Dict]:
        """Получение фактов агента"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM facts 
                WHERE agent_id = ? 
                ORDER BY created_at DESC
                ''', (agent_id,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения фактов: {e}")
            return []

    def get_facts_by_variable(self, variable_name: str, agent_id: str = None) -> List[Dict]:
        """Получение фактов по имени переменной"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if agent_id:
                cursor.execute('''
                    SELECT * FROM facts 
                    WHERE variable_name = ? AND agent_id = ?
                    ORDER BY confidence DESC
                    ''', (variable_name, agent_id))
            else:
                cursor.execute('''
                    SELECT * FROM facts 
                    WHERE variable_name = ? 
                    ORDER BY confidence DESC
                    ''', (variable_name,))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения фактов: {e}")
            return []

    def get_all_facts(self) -> List[Dict]:
        """Получение всех фактов"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM facts ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения фактов: {e}")
            return []

