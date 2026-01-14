import sqlite3
import uuid
from typing import Optional, Dict, List


class AgentService:
    """CRUD операции для агентов"""

    def create_agent(self, name: str, domain_id: str = None,
                     description: str = "") -> Optional[Dict]:
        """Создание нового агента"""
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO agents (id, name, domain_id, description)
                VALUES (?, ?, ?, ?)
                ''', (agent_id, name, domain_id, description))

            # Обновляем счетчик агентов в домене
            if domain_id:
                cursor.execute('''
                    UPDATE domains 
                    SET agents_count = agents_count + 1 
                    WHERE id = ?
                    ''', (domain_id,))

            conn.commit()
            conn.close()

            return self.get_agent(agent_id)

        except sqlite3.Error as e:
            print(f"Ошибка создания агента: {e}")
            return None

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Получение агента по ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"Ошибка получения агента: {e}")
            return None

    def get_agents_by_domain(self, domain_id: str) -> List[Dict]:
        """Получение агентов домена"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM agents 
                WHERE domain_id = ? 
                ORDER BY name
                ''', (domain_id,))
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения агентов: {e}")
            return []

    def get_all_agents(self) -> List[Dict]:
        """Получение всех агентов"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM agents ORDER BY name')
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"Ошибка получения агентов: {e}")
            return []