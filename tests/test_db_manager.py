import sqlite3
from typing import Optional, Dict

import uuid
from database.db_manager import DatabaseManager


class TestDatabaseManager:
    """Тесты менеджера базы данных"""

    def test_init_database(self, temp_db):
        """Тест инициализации базы данных"""
        assert temp_db is not None
        # Проверяем, что таблицы созданы
        conn = temp_db._get_connection()
        cursor = conn.cursor()

        tables = ['domains', 'agents', 'rules', 'facts']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cursor.fetchone() is not None

        conn.close()

    def create_domain(self, name: str, description: str = "") -> Optional[Dict]:
        """Создание новой предметной области"""
        # Сначала проверяем, не существует ли уже такая область
        existing = self.get_domain_by_name(name)
        if existing:
            return existing

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

    def test_create_duplicate_domain(self, temp_db):
        """Тест создания дублирующей области"""
        domain1 = temp_db.create_domain('Медицина', 'Описание')
        domain2 = temp_db.create_domain('Медицина', 'Другое описание')

        # Должен вернуть существующую область, а не создавать новую
        assert domain1 is not None
        assert domain2 is not None
        assert domain1['id'] == domain2['id']
        assert domain1['name'] == domain2['name']

    def test_get_domain_by_name(self, temp_db):
        """Тест получения области по имени"""
        temp_db.create_domain('Медицина', 'Медицинская диагностика')
        domain = temp_db.get_domain_by_name('Медицина')

        assert domain is not None
        assert domain['name'] == 'Медицина'

    def test_get_all_domains(self, temp_db):
        """Тест получения всех областей"""
        temp_db.create_domain('Медицина', 'Описание 1')
        temp_db.create_domain('Техника', 'Описание 2')

        domains = temp_db.get_all_domains()
        assert len(domains) >= 2

    def test_create_agent(self, temp_db):
        """Тест создания агента"""
        domain = temp_db.create_domain('Медицина', 'Описание')
        agent = temp_db.create_agent('Доктор Иванов', domain['id'], 'Главный врач')

        assert agent is not None
        assert agent['name'] == 'Доктор Иванов'
        assert agent['domain_id'] == domain['id']
        assert agent['description'] == 'Главный врач'

    def create_agent(self, name: str, domain_id: str = None, description: str = "") -> Optional[Dict]:
        """Создание нового агента"""
        # Сначала проверяем, не существует ли уже такой агент
        existing = self.get_agent_by_name(name, domain_id)
        if existing:
            return existing

        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agents (id, name, domain_id, description)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, name, domain_id, description))
            conn.commit()
            conn.close()
            return self.get_agent(agent_id)
        except sqlite3.Error as e:
            print(f"Ошибка создания агента: {e}")
            return None

    def get_agent_by_name(self, name: str, domain_id: str = None) -> Optional[Dict]:
        """Получение агента по имени и домену"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            if domain_id:
                cursor.execute('SELECT * FROM agents WHERE name = ? AND domain_id = ?', (name, domain_id))
            else:
                cursor.execute('SELECT * FROM agents WHERE name = ?', (name,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Ошибка получения агента по имени: {e}")
            return None

    def test_get_agents_by_domain(self, temp_db):
        """Тест получения агентов по области"""
        domain = temp_db.create_domain('Медицина', 'Описание')
        temp_db.create_agent('Доктор Иванов', domain['id'], 'Описание')
        temp_db.create_agent('Доктор Петров', domain['id'], 'Описание')

        agents = temp_db.get_agents_by_domain(domain['id'])
        assert len(agents) == 2

    def test_save_rule(self, temp_db, sample_agent):
        """Тест сохранения правила"""
        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }

        rule = temp_db.save_rule(rule_data)
        assert rule is not None
        assert rule['name'] == 'Тестовое правило'
        assert rule['condition'] == 'температура > 38.0'
        assert rule['action'] == 'состояние = лихорадка'
        assert rule['priority'] == 5

    def test_save_rule_without_agent(self, temp_db):
        """Тест сохранения правила без агента"""

        def save_rule(self, rule_data: Dict) -> Optional[Dict]:
            """Сохранение правила"""
            # Проверяем обязательные поля
            required = ['condition', 'action']
            for field in required:
                if field not in rule_data:
                    print(f"Ошибка: отсутствует обязательное поле '{field}'")
                    return None

            # agent_id не обязателен, но если указан - проверяем
            if 'agent_id' in rule_data and rule_data['agent_id']:
                # Проверяем существование агента
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM agents WHERE id = ?', (rule_data['agent_id'],))
                if not cursor.fetchone():
                    conn.close()
                    print(f"Агент с ID {rule_data['agent_id']} не существует")
                    return None
                conn.close()

            # Генерируем ID если нет
            if 'id' not in rule_data:
                rule_data['id'] = str(uuid.uuid4())

        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5
        }

        # Если агент не указан, правило должно сохраниться
        rule = temp_db.save_rule(rule_data)
        assert rule is not None

    def test_get_rules_by_agent(self, temp_db, sample_agent):
        """Тест получения правил агента"""
        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }

        temp_db.save_rule(rule_data)
        rules = temp_db.get_rules_by_agent(sample_agent['id'])

        assert len(rules) == 1
        assert rules[0]['name'] == 'Тестовое правило'

    def test_update_rule_priority(self, temp_db, sample_agent):
        """Тест обновления приоритета правила"""
        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }

        rule = temp_db.save_rule(rule_data)
        assert rule['priority'] == 5

        success = temp_db.update_rule_priority(rule['id'], 9)
        assert success is True

        updated_rule = temp_db.get_rule(rule['id'])
        assert updated_rule['priority'] == 9

    def test_delete_rule(self, temp_db, sample_agent):
        """Тест удаления правила"""
        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }

        rule = temp_db.save_rule(rule_data)
        assert rule is not None

        success = temp_db.delete_rule(rule['id'])
        assert success is True

        deleted_rule = temp_db.get_rule(rule['id'])
        assert deleted_rule is None

    def test_save_fact(self, temp_db, sample_agent):
        """Тест сохранения факта"""
        fact_data = {
            'variable_name': 'температура',
            'value': '39.5',
            'confidence': 0.95,
            'agent_id': sample_agent['id']
        }

        fact = temp_db.save_fact(fact_data)
        assert fact is not None
        assert fact['variable_name'] == 'температура'
        assert fact['value'] == '39.5'
        assert fact['confidence'] == 0.95

    def test_update_fact(self, temp_db, sample_agent):
        """Тест обновления факта"""
        fact_data = {
            'variable_name': 'температура',
            'value': '39.5',
            'confidence': 0.95,
            'agent_id': sample_agent['id']
        }

        fact = temp_db.save_fact(fact_data)
        assert fact['value'] == '39.5'

        success = temp_db.update_fact(fact['id'], 'температура', '40.0', 0.98)
        assert success is True

        updated_fact = temp_db.get_fact(fact['id'])
        assert updated_fact['value'] == '40.0'
        assert updated_fact['confidence'] == 0.98

    def test_delete_fact(self, temp_db, sample_agent):
        """Тест удаления факта"""
        fact_data = {
            'variable_name': 'температура',
            'value': '39.5',
            'confidence': 0.95,
            'agent_id': sample_agent['id']
        }

        fact = temp_db.save_fact(fact_data)
        assert fact is not None

        success = temp_db.delete_fact(fact['id'])
        assert success is True

        deleted_fact = temp_db.get_fact(fact['id'])
        assert deleted_fact is None

    def test_get_statistics(self, temp_db, sample_agent):
        """Тест получения статистики"""
        # Создаем данные
        domain = temp_db.create_domain('Статистика', 'Тест')
        temp_db.create_agent('Агент 1', domain['id'], 'Описание')

        rule_data = {
            'name': 'Правило 1',
            'condition': 'a > b',
            'action': 'c = d',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }
        temp_db.save_rule(rule_data)

        fact_data = {
            'variable_name': 'переменная',
            'value': 'значение',
            'confidence': 0.9,
            'agent_id': sample_agent['id']
        }
        temp_db.save_fact(fact_data)

        stats = temp_db.get_statistics()
        assert stats['domains'] >= 1
        assert stats['agents'] >= 1
        assert stats['rules'] >= 1
        assert stats['facts'] >= 1

    def test_export_import_json(self, temp_db, tmp_path, sample_agent):
        """Тест экспорта и импорта JSON"""
        # Создаем данные
        domain = temp_db.create_domain('Экспорт', 'Тест экспорта')
        agent = temp_db.create_agent('Тестовый агент', domain['id'], 'Описание')

        rule_data = {
            'name': 'Правило экспорта',
            'condition': 'a > b',
            'action': 'c = d',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': agent['id']
        }
        temp_db.save_rule(rule_data)

        # Экспортируем
        json_file = tmp_path / "test_export.json"
        success = temp_db.export_to_json(str(json_file))
        assert success is True
        assert json_file.exists()

        # Импортируем в новую БД
        new_db = DatabaseManager(str(tmp_path / "new_db.sqlite3"))
        success = new_db.import_from_json(str(json_file))
        assert success is True

        # Проверяем импорт
        domains = new_db.get_all_domains()
        assert len(domains) >= 1
        agents = new_db.get_all_agents()
        assert len(agents) >= 1