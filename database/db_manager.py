import csv
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from database.interfaces.agent_repository_interface import IAgentRepository
from database.interfaces.domain_repository_interface import IDomainRepository
from database.interfaces.fact_repository_interface import IFactRepository
from database.interfaces.rule_repository_interface import IRuleRepository
from database.interfaces.statistics_repository_interface import IStatisticsRepository
from database.repositories.agent_repository import AgentRepository
from database.repositories.domain_repository import DomainRepository
from database.repositories.fact_repository import FactRepository
from database.repositories.rule_repository import RuleRepository
from database.repositories.statistics_repository import StatisticsRepository


class DatabaseManager(AgentRepository, DomainRepository, FactRepository,
                      RuleRepository, StatisticsRepository, IStatisticsRepository):
    """Менеджер базы данных SQLite"""

    def __init__(self, db_path: str = None):
        """Инициализация менеджера БД"""

        if db_path is None:
            db_path = "knowledge_base.sqlite3"

        self.db_path = Path(db_path)
        self._init_database()

        self.agent_repository: IAgentRepository = AgentRepository(self.db_path)
        self.domain_repository: IDomainRepository = DomainRepository(self.db_path)
        self.rule_repository: IRuleRepository = RuleRepository(self.db_path)
        self.fact_repository: IFactRepository = FactRepository(self.db_path)
        self.statistics_repository: IStatisticsRepository = StatisticsRepository(self.db_path)

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

    def export_to_json(self, filename: str) -> bool:
        """Экспорт данных в JSON"""
        try:
            data = {
                'domains': self.get_all_domains(),
                'agents': self.get_all_agents(),
                'rules': self.get_all_rules(),
                'facts': self.get_all_facts(),
                'export_date': datetime.now().isoformat()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Ошибка экспорта в JSON: {e}")
            return False

    def import_from_json(self, filename: str) -> bool:
        """Импорт данных из JSON с проверкой существующих записей"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Импортируем области (только новые)
                for domain in data.get('domains', []):
                    # Проверяем, существует ли уже такая область
                    existing = self.get_domain_by_name(domain.get('name'))
                    if existing:
                        print(f"Область '{domain.get('name')}' уже существует, пропускаем")
                        continue

                    cursor.execute('''
                        INSERT INTO domains (id, name, description, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        domain.get('id', str(uuid.uuid4())),
                        domain.get('name'),
                        domain.get('description'),
                        domain.get('created_at', datetime.now().isoformat())
                    ))

                # Импортируем агентов (только новых)
                for agent in data.get('agents', []):
                    # Получаем ID домена
                    domain_id = agent.get('domain_id')
                    if domain_id:
                        domain = self.get_domain(domain_id)
                        if not domain:
                            # Пробуем найти домен по имени
                            domain = self.get_domain_by_name(agent.get('domain_name', 'Общая предметная область'))
                            if domain:
                                domain_id = domain['id']
                            else:
                                # Создаем домен по умолчанию
                                default_domain = self.create_domain(
                                    name="Общая предметная область",
                                    description="Автоматически созданный домен для импорта"
                                )
                                if default_domain:
                                    domain_id = default_domain['id']
                                else:
                                    domain_id = None

                    # Проверяем, существует ли уже такой агент
                    existing = self.get_agent_by_name(agent.get('name'), domain_id)
                    if existing:
                        print(f"Агент '{agent.get('name')}' уже существует, пропускаем")
                        continue

                    cursor.execute('''
                        INSERT INTO agents (id, name, domain_id, description, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        agent.get('id', str(uuid.uuid4())),
                        agent.get('name'),
                        domain_id,
                        agent.get('description'),
                        agent.get('created_at', datetime.now().isoformat())
                    ))

                # Получаем ID агентов для привязки правил
                agent_map = {}
                for agent in data.get('agents', []):
                    # Находим домен
                    domain_id = agent.get('domain_id')
                    if domain_id:
                        domain = self.get_domain(domain_id)
                        if not domain:
                            domain = self.get_domain_by_name('Общая предметная область')
                            if domain:
                                domain_id = domain['id']

                    existing = self.get_agent_by_name(agent.get('name'), domain_id)
                    if existing:
                        agent_map[agent.get('id')] = existing['id']
                    else:
                        # Создаем агента из данных
                        new_agent = self.create_agent(
                            name=agent.get('name'),
                            domain_id=domain_id,
                            description=agent.get('description')
                        )
                        if new_agent:
                            agent_map[agent.get('id')] = new_agent['id']

                # Импортируем правила
                for rule in data.get('rules', []):
                    agent_id = rule.get('agent_id')
                    # Преобразуем старый ID агента в новый
                    if agent_id and agent_id in agent_map:
                        agent_id = agent_map[agent_id]
                    else:
                        agent_id = None

                    # Проверяем, существует ли уже такое правило (по уникальности условия и действия)
                    cursor.execute('''
                        SELECT id FROM rules 
                        WHERE condition = ? AND action = ? AND agent_id = ?
                    ''', (rule.get('condition', ''), rule.get('action', ''), agent_id))

                    existing = cursor.fetchone()
                    if existing:
                        print(f"Правило '{rule.get('name', '')}' уже существует, пропускаем")
                        continue

                    cursor.execute('''
                        INSERT INTO rules 
                        (id, name, condition, action, rule_type, priority, agent_id, source_file, author, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        rule.get('id', str(uuid.uuid4())),
                        rule.get('name', ''),
                        rule.get('condition', ''),
                        rule.get('action', ''),
                        rule.get('rule_type', 'conditional'),
                        rule.get('priority', 1),
                        agent_id,
                        rule.get('source_file', ''),
                        rule.get('author', ''),
                        rule.get('created_at', datetime.now().isoformat())
                    ))

                # Импортируем факты
                for fact in data.get('facts', []):
                    agent_id = fact.get('agent_id')
                    if agent_id and agent_id in agent_map:
                        agent_id = agent_map[agent_id]
                    else:
                        agent_id = None

                    # Проверяем, существует ли уже такой факт
                    cursor.execute('''
                        SELECT id FROM facts 
                        WHERE variable_name = ? AND agent_id = ?
                    ''', (fact.get('variable_name'), agent_id))

                    existing = cursor.fetchone()
                    if existing:
                        print(f"Факт '{fact.get('variable_name')}' уже существует, пропускаем")
                        continue

                    cursor.execute('''
                        INSERT INTO facts 
                        (id, variable_name, value, confidence, agent_id, source_file, author, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fact.get('id', str(uuid.uuid4())),
                        fact.get('variable_name'),
                        fact.get('value', ''),
                        fact.get('confidence', 1.0),
                        agent_id,
                        fact.get('source_file', ''),
                        fact.get('author', ''),
                        fact.get('created_at', datetime.now().isoformat())
                    ))

            return True
        except Exception as e:
            print(f"Ошибка импорта из JSON: {e}")
            import traceback
            traceback.print_exc()
            return False

    def export_to_csv(self, filename: str) -> bool:
        """Экспорт данных в CSV"""
        try:
            rules = self.get_all_rules()

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if rules:
                    writer = csv.DictWriter(f, fieldnames=rules[0].keys())
                    writer.writeheader()
                    writer.writerows(rules)

            return True
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return False
