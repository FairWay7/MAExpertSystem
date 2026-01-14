import sqlite3
from typing import Dict


class StatisticsRepository:
    def get_statistics(self) -> Dict:
        """Получение статистики БД"""
        stats = {}

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Подсчет записей
            cursor.execute("SELECT COUNT(*) FROM domains")
            stats['domains'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM agents")
            stats['agents'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM rules")
            stats['rules'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM facts")
            stats['facts'] = cursor.fetchone()[0]

            # Статистика по типам правил
            cursor.execute("""
            SELECT rule_type, COUNT(*) as count 
            FROM rules 
            GROUP BY rule_type
            """)
            stats['rules_by_type'] = dict(cursor.fetchall())

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка получения статистики: {e}")

        return stats