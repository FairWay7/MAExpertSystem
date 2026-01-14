import sqlite3
import json
from datetime import datetime
from pathlib import Path
import agent_repository
import domain_repository
import fact_repository
import rule_repository
import statistics_repository
from typing import List, Dict


class DatabaseManager:
    """Менеджер базы данных SQLite"""

    def __init__(self, db_path: str = None):
        """Инициализация менеджера БД"""

        if db_path is None:
            db_path = "knowledge_base.sqlite3"

        self.db_path = Path(db_path)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Создание соединения с БД"""

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Для доступа по имени столбцов
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_database(self):
        """Инициализация структуры БД"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица доменов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            rules_count INTEGER DEFAULT 0,
            facts_count INTEGER DEFAULT 0,
            agents_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица агентов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain_id TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE SET NULL
        )
        ''')

        # Таблица правил
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id TEXT PRIMARY KEY,
            name TEXT,
            condition TEXT NOT NULL,
            action TEXT NOT NULL,
            rule_type TEXT,
            priority INTEGER DEFAULT 1,
            confidence REAL DEFAULT 1.0,
            source_file TEXT,
            author TEXT,
            tags TEXT,
            agent_id TEXT NOT NULL,
            domain_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE SET NULL
        )
        ''')

        # Таблица фактов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            id TEXT PRIMARY KEY,
            variable_name TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            source_file TEXT,
            author TEXT,
            is_derived INTEGER DEFAULT 0,
            agent_id TEXT NOT NULL,
            domain_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE SET NULL
        )
        ''')

        # Индексы для ускорения поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_agent ON rules(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rules_domain ON rules(domain_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_agent ON facts(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_variable ON facts(variable_name)')

        conn.commit()
        conn.close()

        print(f"База данных инициализирована: {self.db_path}")


    # Экспорт/импорт

    def export_to_json(self, output_file: str) -> bool:
        """Экспорт всей БД в JSON"""
        try:
            data = {
                'export_date': datetime.now().isoformat(),
                'domains': self.get_all_domains(),
                'agents': self.get_all_agents(),
                'rules': self.get_all_rules(),
                'facts': self.get_all_facts()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"База данных экспортирована в {output_file}")
            return True

        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

    def import_from_json(self, input_file: str) -> bool:
        """Импорт БД из JSON"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Импортируем домены
            for domain_data in data.get('domains', []):
                self.create_domain(
                    name=domain_data['name'],
                    description=domain_data.get('description', '')
                )

            # Импортируем агентов
            for agent_data in data.get('agents', []):
                self.create_agent(
                    name=agent_data['name'],
                    domain_id=agent_data.get('domain_id'),
                    description=agent_data.get('description', '')
                )

            # Импортируем правила
            for rule_data in data.get('rules', []):
                self.save_rule(rule_data)

            # Импортируем факты
            for fact_data in data.get('facts', []):
                self.save_fact(fact_data)

            print(f"База данных импортирована из {input_file}")
            return True

        except Exception as e:
            print(f"Ошибка импорта: {e}")
            return False

    # ===== Поиск =====

    def search_rules(self, query: str, agent_ids: List[str] = None) -> List[Dict]:
        """Поиск правил по тексту"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query_lower = f"%{query.lower()}%"

            if agent_ids:
                # Создаем строку с placeholders
                placeholders = ','.join(['?'] * len(agent_ids))
                sql = f'''
                SELECT * FROM rules 
                WHERE (LOWER(condition) LIKE ? OR LOWER(action) LIKE ?) 
                AND agent_id IN ({placeholders})
                ORDER BY priority DESC
                '''
                params = [query_lower, query_lower] + agent_ids
            else:
                sql = '''
                SELECT * FROM rules 
                WHERE LOWER(condition) LIKE ? OR LOWER(action) LIKE ? 
                ORDER BY priority DESC
                '''
                params = [query_lower, query_lower]

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            rules = []
            for row in rows:
                rule = dict(row)
                if rule.get('tags'):
                    try:
                        rule['tags'] = json.loads(rule['tags'])
                    except:
                        rule['tags'] = []
                rules.append(rule)

            return rules

        except sqlite3.Error as e:
            print(f"Ошибка поиска правил: {e}")
            return []