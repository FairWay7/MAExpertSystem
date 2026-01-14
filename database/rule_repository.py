import json
import sqlite3
import uuid
from typing import Optional, Dict, List


class Repository:
    # CRUD операции для правил

    def save_rule(self, rule_data: Dict) -> Optional[Dict]:
        """Сохранение правила"""
        # Проверяем обязательные поля
        required = ['condition', 'action', 'agent_id']
        for field in required:
            if field not in rule_data:
                print(f"Ошибка: отсутствует обязательное поле '{field}'")
                return None

        # Генерируем ID если нет
        if 'id' not in rule_data:
            rule_data['id'] = str(uuid.uuid4())

        # Преобразуем теги в JSON
        tags = rule_data.get('tags', [])
        if isinstance(tags, list):
            tags_json = json.dumps(tags, ensure_ascii=False)
        else:
            tags_json = tags or ''

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO rules (
                    id, name, condition, action, rule_type, priority, confidence,
                    source_file, author, tags, agent_id, domain_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                rule_data['id'],
                rule_data.get('name', ''),
                rule_data['condition'],
                rule_data['action'],
                rule_data.get('rule_type', 'conditional'),
                rule_data.get('priority', 1),
                rule_data.get('confidence', 1.0),
                rule_data.get('source_file', ''),
                rule_data.get('author', 'system'),
                tags_json,
                rule_data['agent_id'],
                rule_data.get('domain_id')
            ))

            # Обновляем счетчик правил в домене
            if rule_data.get('domain_id'):
                cursor.execute('''
                    UPDATE domains 
                    SET rules_count = rules_count + 1 
                    WHERE id = ?
                    ''', (rule_data['domain_id'],))

            conn.commit()
            conn.close()

            return self.get_rule(rule_data['id'])

        except sqlite3.Error as e:
            print(f"Ошибка сохранения правила: {e}")
            return None

    def get_rule(self, rule_id: str) -> Optional[Dict]:
        """Получение правила по ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM rules WHERE id = ?', (rule_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                rule = dict(row)
                # Парсим теги из JSON
                if rule.get('tags'):
                    try:
                        rule['tags'] = json.loads(rule['tags'])
                    except:
                        rule['tags'] = []
                return rule
            return None

        except sqlite3.Error as e:
            print(f"Ошибка получения правила: {e}")
            return None

    def get_rules_by_agent(self, agent_id: str) -> List[Dict]:
        """Получение правил агента"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM rules 
                WHERE agent_id = ? 
                ORDER BY priority DESC, created_at DESC
                ''', (agent_id,))
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
            print(f"Ошибка получения правил: {e}")
            return []

    def get_rules_by_domain(self, domain_id: str) -> List[Dict]:
        """Получение правил домена"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM rules 
                WHERE domain_id = ? 
                ORDER BY priority DESC, created_at DESC
                ''', (domain_id,))
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
            print(f"Ошибка получения правил: {e}")
            return []

    def get_all_rules(self) -> List[Dict]:
        """Получение всех правил"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM rules ORDER BY created_at DESC')
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
            print(f"Ошибка получения правил: {e}")
            return []

    def update_rule_priority(self, rule_id: str, priority: int) -> bool:
        """Обновление приоритета правила"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE rules SET priority = ? WHERE id = ?
                ''', (priority, rule_id))

            conn.commit()
            conn.close()

            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Ошибка обновления приоритета: {e}")
            return False

    def delete_rule(self, rule_id: str) -> bool:
        """Удаление правила"""
        try:
            # Сначала получаем правило чтобы узнать domain_id
            rule = self.get_rule(rule_id)

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM rules WHERE id = ?', (rule_id,))

            # Обновляем счетчик правил в домене
            if rule and rule.get('domain_id'):
                cursor.execute('''
                    UPDATE domains 
                    SET rules_count = rules_count - 1 
                    WHERE id = ?
                    ''', (rule['domain_id'],))

            conn.commit()
            conn.close()

            return True

        except sqlite3.Error as e:
            print(f"Ошибка удаления правила: {e}")
            return False

    # Анализ правил

    def find_similar_rules(self, agent_id: str = None,
                           threshold: float = 0.7) -> List[Dict]:
        """Поиск схожих правил"""
        # Получаем правила для анализа
        if agent_id:
            rules = self.get_rules_by_agent(agent_id)
        else:
            rules = self.get_all_rules()

        similar_pairs = []

        # Попарное сравнение
        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                similarity = self._calculate_similarity(
                    rules[i]['condition'], rules[j]['condition']
                )

                if similarity >= threshold:
                    similar_pairs.append({
                        'rule1': rules[i],
                        'rule2': rules[j],
                        'similarity': similarity,
                        'type': self._determine_similarity_type(
                            rules[i], rules[j]
                        )
                    })

        return similar_pairs

    def find_conflicting_rules(self, agent_id: str = None) -> List[Dict]:
        """Поиск конфликтных правил"""
        # Получаем правила для анализа
        if agent_id:
            rules = self.get_rules_by_agent(agent_id)
        else:
            rules = self.get_all_rules()

        conflicting_pairs = []

        # Попарное сравнение
        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                # Проверяем схожесть условий
                condition_sim = self._calculate_similarity(
                    rule1['condition'], rule2['condition']
                )

                # Если условия схожи, но действия разные - конфликт
                if condition_sim > 0.8 and rule1['action'] != rule2['action']:
                    conflicting_pairs.append({
                        'rule1': rule1,
                        'rule2': rule2,
                        'condition_similarity': condition_sim,
                        'conflict_type': 'different_actions'
                    })

        return conflicting_pairs

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Вычисление схожести текстов"""
        if not text1 or not text2:
            return 0.0

        # Приводим к нижнему регистру
        text1 = text1.lower()
        text2 = text2.lower()

        # Разбиваем на слова
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        # Коэффициент Жаккара
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _determine_similarity_type(self, rule1: Dict, rule2: Dict) -> str:
        """Определение типа схожести"""
        cond_sim = self._calculate_similarity(rule1['condition'], rule2['condition'])
        act_sim = self._calculate_similarity(rule1['action'], rule2['action'])

        if cond_sim > 0.8 and act_sim > 0.8:
            return 'identical'
        elif cond_sim > 0.8:
            return 'same_condition'
        elif act_sim > 0.8:
            return 'same_action'
        else:
            return 'partial'