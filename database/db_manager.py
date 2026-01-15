import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from database.agent_repository import AgentRepository
from database.domain_repository import DomainRepository
from database.fact_repository import FactRepository
from database.rule_repository import RuleRepository
from database.statistics_repository import StatisticsRepository


class DatabaseManager:
    """Менеджер базы данных SQLite"""

    def __init__(self, db_path: str = None):
        """Инициализация менеджера БД"""

        if db_path is None:
            db_path = "knowledge_base.sqlite3"

        self.db_path = Path(db_path)
        self._init_database()

        self.agent_repository = AgentRepository(self.db_path)
        self.domain_repository = DomainRepository(self.db_path)
        self.rule_repository = RuleRepository(self.db_path)
        self.fact_repository = FactRepository(self.db_path)
        self.statistics_repository = StatisticsRepository(self.db_path)

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



    def create_agent(self, name: str, domain_id: str = None, description: str = "") -> Optional[Dict]:
        return self.agent_repository.create_agent(name, domain_id, description)

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        return self.agent_repository.get_agent(agent_id)



    def get_agents_by_domain(self, domain_id: str) -> List[Dict]:
        return self.agent_repository.get_agents_by_domain(domain_id)

    def get_all_agents(self) -> List[Dict]:
        return self.agent_repository.get_all_agents()

    def create_domain(self, name: str, description: str = "") -> Optional[Dict]:
        return self.domain_repository.create_domain(name, description)

    def get_all_domains(self) -> List[Dict]:
        return self.domain_repository.get_all_domains()

    def get_domain(self, domain_id: str) -> Optional[Dict]:
        return self.domain_repository.get_domain(domain_id)

    def get_domain_by_name(self, name: str) -> Optional[Dict]:
        return self.domain_repository.get_domain_by_name(name)



    def save_fact(self, fact_data: Dict) -> Optional[Dict]:
        return self.fact_repository.save_fact(fact_data)

    def get_fact(self, fact_id: str) -> Optional[Dict]:
        return self.fact_repository.get_fact(fact_id)

    def get_facts_by_agent(self, agent_id: str) -> List[Dict]:
        return self.fact_repository.get_facts_by_agent(agent_id)

    def get_facts_by_variable(self, variable_name: str, agent_id: str = None) -> List[Dict]:
        return self.fact_repository.get_facts_by_variable(variable_name, agent_id)

    def get_all_facts(self) -> List[Dict]:
        return self.fact_repository.get_all_facts()



    def save_rule(self, rule_data: Dict) -> Optional[Dict]:
        return self.rule_repository.save_rule(rule_data)

    def get_rule(self, rule_id: str) -> Optional[Dict]:
        return self.rule_repository.get_rule(rule_id)

    def get_rules_by_agent(self, agent_id: str) -> List[Dict]:
        return self.rule_repository.get_rules_by_agent(agent_id)

    def get_rules_by_domain(self, domain_id: str) -> List[Dict]:
        return self.rule_repository.get_rules_by_domain(domain_id)

    def get_all_rules(self) -> List[Dict]:
        return self.rule_repository.get_all_rules()

    def update_rule_priority(self, rule_id: str, priority: int) -> bool:
        return self.rule_repository.update_rule_priority(rule_id, priority)

    def delete_rule(self, rule_id: str) -> bool:
        return self.rule_repository.delete_rule(rule_id)

    def find_similar_rules(self, agent_id: str = None, threshold: float = 0.7) -> List[Dict]:
        return self.rule_repository.find_similar_rules(agent_id, threshold)

    def find_conflicting_rules(self, agent_id: str = None) -> List[Dict]:
        return self.rule_repository.find_conflicting_rules(agent_id)

    def search_rules(self, query: str, agent_ids: List[str] = None) -> List[Dict]:
        return self.rule_repository.search_rules(query, agent_ids)

    def get_statistics(self) -> Dict:
        return self.statistics_repository.get_statistics()


    __all__ = ['AgentRepository', 'DomainRepository', 'FactRepository', 'RuleRepository', 'StatisticsRepository']