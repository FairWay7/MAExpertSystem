from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, Counter
import re
from datetime import datetime


class TraceAnalyzer:
    """
    Анализатор базы знаний для трассировки правил агента.
    Выявляет различные типы проблем и генерирует рекомендации.
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def analyze_agent_knowledge_base(self, agent_id: str) -> Dict:
        """
        Комплексный анализ базы знаний агента.

        Args:
            agent_id: ID агента для анализа

        Returns:
            Словарь с результатами анализа
        """
        # Получаем все правила агента
        rules = self.db_manager.get_rules_by_agent(agent_id)

        if not rules:
            return self._empty_analysis_result(agent_id)

        # Получаем факты агента
        facts = self.db_manager.get_facts_by_agent(agent_id)

        # Получаем информацию об агенте
        agent = self.db_manager.get_agent(agent_id)
        agent_name = agent['name'] if agent else "Неизвестный агент"

        # Выполняем различные виды анализа
        results = {
            'agent_id': agent_id,
            'agent_name': agent_name,
            'total_rules': len(rules),
            'total_facts': len(facts),
            'analysis_date': datetime.now().isoformat(),

            # Статистика правил
            'rule_statistics': self._analyze_rule_statistics(rules),

            # Анализ условий
            'condition_analysis': self._analyze_conditions(rules),

            # Анализ действий
            'action_analysis': self._analyze_actions(rules),

            # Схожие правила
            'similar_rules': self._find_similar_rules_detailed(rules),

            # Конфликтные правила
            'conflicting_rules': self._find_conflicting_rules_detailed(rules),

            # Избыточные правила
            'redundant_rules': self._find_redundant_rules(rules),

            # Неполные правила (слабые условия)
            'weak_rules': self._find_weak_rules(rules),

            # Цепочки правил
            'rule_chains': self._find_rule_chains(rules),

            # Переменные и их использование
            'variable_usage': self._analyze_variable_usage(rules),

            # Рекомендации
            'recommendations': []
        }

        # Генерируем рекомендации на основе анализа
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _empty_analysis_result(self, agent_id: str) -> Dict:
        """Возвращает пустой результат анализа"""
        agent = self.db_manager.get_agent(agent_id)
        return {
            'agent_id': agent_id,
            'agent_name': agent['name'] if agent else "Неизвестный агент",
            'total_rules': 0,
            'total_facts': 0,
            'analysis_date': datetime.now().isoformat(),
            'rule_statistics': {},
            'condition_analysis': {},
            'action_analysis': {},
            'similar_rules': [],
            'conflicting_rules': [],
            'redundant_rules': [],
            'weak_rules': [],
            'rule_chains': [],
            'variable_usage': {},
            'recommendations': [
                'База знаний пуста. Добавьте правила для анализа.',
                'Создайте правила через анализ текста или вручную.'
            ]
        }

    def _analyze_rule_statistics(self, rules: List[Dict]) -> Dict:
        """Анализ статистики правил"""
        stats = {
            'total': len(rules),
            'by_type': Counter(),
            'by_priority': Counter(),
            'avg_priority': 0,
            'min_priority': 0,
            'max_priority': 0,
            'priority_distribution': {
                'low': 0,  # 1-3
                'medium': 0,  # 4-7
                'high': 0  # 8-10
            }
        }

        total_priority = 0

        for rule in rules:
            rule_type = rule.get('rule_type', 'conditional')
            stats['by_type'][rule_type] += 1

            priority = rule.get('priority', 1)
            stats['by_priority'][priority] += 1
            total_priority += priority

            if priority <= 3:
                stats['priority_distribution']['low'] += 1
            elif priority <= 7:
                stats['priority_distribution']['medium'] += 1
            else:
                stats['priority_distribution']['high'] += 1

        if rules:
            stats['avg_priority'] = round(total_priority / len(rules), 2)
            stats['min_priority'] = min(stats['by_priority'].keys())
            stats['max_priority'] = max(stats['by_priority'].keys())

        # Преобразуем Counter в dict для сериализации
        stats['by_type'] = dict(stats['by_type'])
        stats['by_priority'] = dict(stats['by_priority'])

        return stats

    def _analyze_conditions(self, rules: List[Dict]) -> Dict:
        """Анализ условий правил"""
        analysis = {
            'unique_conditions': 0,
            'duplicate_conditions': 0,
            'condition_lengths': {
                'min': 0,
                'max': 0,
                'avg': 0
            },
            'most_common_variables': Counter(),
            'condition_complexity': {
                'simple': 0,  # 1-2 условия
                'medium': 0,  # 3-5 условий
                'complex': 0  # >5 условий
            }
        }

        conditions = []
        total_length = 0

        for rule in rules:
            condition = rule.get('condition', '')
            conditions.append(condition)
            total_length += len(condition)

            # Извлекаем переменные из условия
            variables = self._extract_variables(condition)
            analysis['most_common_variables'].update(variables)

            # Оцениваем сложность
            complexity = len(self._split_conditions(condition))
            if complexity <= 2:
                analysis['condition_complexity']['simple'] += 1
            elif complexity <= 5:
                analysis['condition_complexity']['medium'] += 1
            else:
                analysis['condition_complexity']['complex'] += 1

        # Уникальные условия
        analysis['unique_conditions'] = len(set(conditions))
        analysis['duplicate_conditions'] = len(conditions) - analysis['unique_conditions']

        # Длина условий
        if conditions:
            lengths = [len(c) for c in conditions]
            analysis['condition_lengths']['min'] = min(lengths)
            analysis['condition_lengths']['max'] = max(lengths)
            analysis['condition_lengths']['avg'] = round(sum(lengths) / len(lengths), 1)

        # Преобразуем Counter в dict
        analysis['most_common_variables'] = dict(analysis['most_common_variables'].most_common(10))

        return analysis

    def _analyze_actions(self, rules: List[Dict]) -> Dict:
        """Анализ действий правил"""
        analysis = {
            'unique_actions': 0,
            'duplicate_actions': 0,
            'action_lengths': {
                'min': 0,
                'max': 0,
                'avg': 0
            },
            'most_common_assignments': Counter(),
            'action_types': {
                'assignment': 0,  # присваивание
                'function': 0,  # вызов функции
                'other': 0
            }
        }

        actions = []
        total_length = 0

        for rule in rules:
            action = rule.get('action', '')
            actions.append(action)
            total_length += len(action)

            # Определяем тип действия
            if '=' in action:
                analysis['action_types']['assignment'] += 1
                var = action.split('=')[0].strip()
                analysis['most_common_assignments'][var] += 1
            elif '(' in action and ')' in action:
                analysis['action_types']['function'] += 1
            else:
                analysis['action_types']['other'] += 1

        # Уникальные действия
        analysis['unique_actions'] = len(set(actions))
        analysis['duplicate_actions'] = len(actions) - analysis['unique_actions']

        # Длина действий
        if actions:
            lengths = [len(a) for a in actions]
            analysis['action_lengths']['min'] = min(lengths)
            analysis['action_lengths']['max'] = max(lengths)
            analysis['action_lengths']['avg'] = round(sum(lengths) / len(lengths), 1)

        # Преобразуем Counter в dict
        analysis['most_common_assignments'] = dict(analysis['most_common_assignments'].most_common(10))

        return analysis

    def _find_similar_rules_detailed(self, rules: List[Dict]) -> List[Dict]:
        """
        Детальный поиск схожих правил с несколькими типами схожести.
        """
        similar_pairs = []

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                # Вычисляем разные типы схожести
                condition_sim = self._calculate_similarity(
                    rule1['condition'], rule2['condition']
                )
                action_sim = self._calculate_similarity(
                    rule1['action'], rule2['action']
                )

                # Определяем тип схожести
                similarity_type = 'none'
                if condition_sim > 0.8 and action_sim > 0.8:
                    similarity_type = 'identical'  # Почти идентичные
                    similarity_score = max(condition_sim, action_sim)
                elif condition_sim > 0.8:
                    similarity_type = 'same_condition'  # Одинаковые условия
                    similarity_score = condition_sim
                elif action_sim > 0.8:
                    similarity_type = 'same_action'  # Одинаковые действия
                    similarity_score = action_sim
                elif condition_sim > 0.6 or action_sim > 0.6:
                    similarity_type = 'partial'  # Частичная схожесть
                    similarity_score = max(condition_sim, action_sim)
                else:
                    continue

                if similarity_type != 'none':
                    similar_pairs.append({
                        'rule1': rule1,
                        'rule2': rule2,
                        'condition_similarity': round(condition_sim, 3),
                        'action_similarity': round(action_sim, 3),
                        'similarity_type': similarity_type,
                        'overall_similarity': round(similarity_score, 3),
                        'recommendation': self._get_similarity_recommendation(
                            similarity_type, rule1, rule2
                        )
                    })

        # Сортируем по убыванию схожести
        similar_pairs.sort(key=lambda x: x['overall_similarity'], reverse=True)

        return similar_pairs

    def _find_conflicting_rules_detailed(self, rules: List[Dict]) -> List[Dict]:
        """
        Детальный поиск конфликтных правил с классификацией конфликтов.
        """
        conflicts = []

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                # Проверяем различные типы конфликтов
                conflict_type = self._detect_conflict_type(rule1, rule2)

                if conflict_type:
                    condition_sim = self._calculate_similarity(
                        rule1['condition'], rule2['condition']
                    )

                    conflicts.append({
                        'rule1': rule1,
                        'rule2': rule2,
                        'conflict_type': conflict_type,
                        'condition_similarity': round(condition_sim, 3),
                        'severity': self._calculate_conflict_severity(rule1, rule2, conflict_type),
                        'description': self._get_conflict_description(conflict_type, rule1, rule2),
                        'recommendation': self._get_conflict_recommendation(conflict_type)
                    })

        # Сортируем по убыванию серьезности
        conflicts.sort(key=lambda x: x['severity'], reverse=True)

        return conflicts

    def _detect_conflict_type(self, rule1: Dict, rule2: Dict) -> Optional[str]:
        """
        Определяет тип конфликта между двумя правилами.
        """
        condition1 = rule1.get('condition', '')
        condition2 = rule2.get('condition', '')
        action1 = rule1.get('action', '')
        action2 = rule2.get('action', '')

        # Проверяем схожесть условий
        condition_sim = self._calculate_similarity(condition1, condition2)

        if condition_sim > 0.7:
            # Извлекаем переменные и значения из действий
            vars1 = self._extract_variables(action1)
            vars2 = self._extract_variables(action2)
            vals1 = self._extract_values(action1)
            vals2 = self._extract_values(action2)

            # Проверяем на противоречивые присваивания
            for var1, val1 in zip(vars1, vals1):
                for var2, val2 in zip(vars2, vals2):
                    if var1 == var2:
                        # Проверяем противоположные значения
                        if self._are_opposite_values(val1, val2):
                            return 'contradictory_assignment'
                        elif val1 != val2:
                            return 'different_assignment'

            # Проверяем на разные действия при схожих условиях
            if action1 != action2 and condition_sim > 0.8:
                # Проверяем, не являются ли действия просто разными формулировками
                if self._calculate_similarity(action1, action2) < 0.5:
                    return 'different_actions'

        # Проверяем на циклическую зависимость
        if self._is_cyclic_dependency(rule1, rule2):
            return 'cyclic_dependency'

        return None

    def _find_redundant_rules(self, rules: List[Dict]) -> List[Dict]:
        """
        Поиск избыточных правил (правил, которые являются следствием других).
        """
        redundant = []

        for i, rule1 in enumerate(rules):
            condition1 = rule1.get('condition', '')
            action1 = rule1.get('action', '')

            for j, rule2 in enumerate(rules):
                if i == j:
                    continue

                condition2 = rule2.get('condition', '')
                action2 = rule2.get('action', '')

                # Проверяем, не является ли правило1 следствием правила2
                if (self._is_condition_subset(condition1, condition2) and
                        action1 == action2):
                    redundant.append({
                        'redundant_rule': rule1,
                        'superset_rule': rule2,
                        'reason': 'Условие правила является подмножеством другого правила с тем же действием',
                        'recommendation': 'Рассмотрите возможность объединения или удаления избыточного правила'
                    })
                    break

                # Проверяем, не является ли правило1 более общим случаем правила2
                if (self._is_condition_subset(condition2, condition1) and
                        action1 == action2):
                    redundant.append({
                        'redundant_rule': rule2,
                        'superset_rule': rule1,
                        'reason': 'Условие правила является подмножеством другого правила с тем же действием',
                        'recommendation': 'Рассмотрите возможность объединения или удаления избыточного правила'
                    })
                    break

        return redundant

    def _find_weak_rules(self, rules: List[Dict]) -> List[Dict]:
        """
        Поиск слабых правил (слишком общие или слишком специфичные).
        """
        weak = []

        for rule in rules:
            condition = rule.get('condition', '')

            # Извлекаем условия
            conditions = self._split_conditions(condition)

            # Слишком простые условия (менее 2 условий)
            if len(conditions) < 2:
                weak.append({
                    'rule': rule,
                    'issue': 'too_simple',
                    'description': 'Правило содержит слишком мало условий (менее 2)',
                    'recommendation': 'Рассмотрите возможность добавления дополнительных условий для повышения точности'
                })
                continue

            # Слишком сложные условия (более 5 условий)
            if len(conditions) > 5:
                weak.append({
                    'rule': rule,
                    'issue': 'too_complex',
                    'description': f'Правило содержит слишком много условий ({len(conditions)})',
                    'recommendation': 'Рассмотрите возможность разбиения правила на несколько более простых правил'
                })
                continue

            # Проверяем на использование общих переменных
            variables = self._extract_variables(condition)
            common_vars = ['температура', 'давление', 'время', 'скорость', 'расстояние']
            common_count = sum(1 for v in variables if v.lower() in common_vars)

            if common_count == len(variables) and len(variables) > 0:
                weak.append({
                    'rule': rule,
                    'issue': 'too_general',
                    'description': 'Правило использует только общие переменные без специфических условий',
                    'recommendation': 'Добавьте более специфические условия для уточнения правила'
                })

        return weak

    def _find_rule_chains(self, rules: List[Dict]) -> List[Dict]:
        """
        Поиск цепочек правил (где действие одного правила является условием другого).
        """
        chains = []

        # Создаем карту действий к правилам
        action_to_rules = defaultdict(list)
        for rule in rules:
            action = rule.get('action', '')
            variables = self._extract_variables(action)
            for var in variables:
                action_to_rules[var].append(rule)

        # Ищем цепочки
        for rule in rules:
            condition = rule.get('condition', '')
            variables = self._extract_variables(condition)

            for var in variables:
                if var in action_to_rules:
                    for prev_rule in action_to_rules[var]:
                        # Избегаем циклов
                        if prev_rule['id'] != rule['id']:
                            chains.append({
                                'source_rule': prev_rule,
                                'target_rule': rule,
                                'variable': var,
                                'chain_type': 'direct',
                                'description': f"Действие правила '{prev_rule.get('name', 'Без названия')}' "
                                               f"используется в условии правила '{rule.get('name', 'Без названия')}' "
                                               f"через переменную '{var}'"
                            })

        return chains

    def _analyze_variable_usage(self, rules: List[Dict]) -> Dict:
        """
        Анализ использования переменных в правилах.
        """
        usage = {
            'variables': {},  # переменная -> {использование в условиях, использование в действиях}
            'unused_variables': [],  # переменные, которые только объявляются, но не используются
            'undefined_variables': []  # переменные, которые используются, но не объявляются
        }

        condition_vars = set()
        action_vars = set()

        for rule in rules:
            condition = rule.get('condition', '')
            action = rule.get('action', '')

            # Извлекаем переменные из условия и действия
            cond_vars = set(self._extract_variables(condition))
            act_vars = set(self._extract_variables(action))

            condition_vars.update(cond_vars)
            action_vars.update(act_vars)

            # Обновляем детальную информацию
            for var in cond_vars:
                if var not in usage['variables']:
                    usage['variables'][var] = {'in_conditions': 0, 'in_actions': 0}
                usage['variables'][var]['in_conditions'] += 1

            for var in act_vars:
                if var not in usage['variables']:
                    usage['variables'][var] = {'in_conditions': 0, 'in_actions': 0}
                usage['variables'][var]['in_actions'] += 1

        # Находим неиспользуемые переменные
        usage['unused_variables'] = list(action_vars - condition_vars)
        usage['undefined_variables'] = list(condition_vars - action_vars)

        return usage

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Вычисление схожести двух текстов (коэффициент Жаккара).
        """
        if not text1 or not text2:
            return 0.0

        # Очищаем тексты
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)

        # Разбиваем на слова
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        # Коэффициент Жаккара
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _normalize_text(self, text: str) -> str:
        """
        Нормализация текста для сравнения.
        """
        # Приводим к нижнему регистру
        text = text.lower()

        # Удаляем знаки препинания
        text = re.sub(r'[^\w\s]', ' ', text)

        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _extract_variables(self, text: str) -> List[str]:
        """
        Извлечение имен переменных из текста.
        """
        # Ищем слова, которые могут быть переменными
        # Переменные обычно состоят из букв, цифр и подчеркиваний
        pattern = r'\b[a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]*\b'
        variables = re.findall(pattern, text)

        # Фильтруем общие слова
        stopwords = {'если', 'то', 'и', 'или', 'не', 'в', 'на', 'с', 'по', 'для',
                     'при', 'когда', 'тогда', 'затем', 'также', 'более', 'менее',
                     'выше', 'ниже', 'равно', 'больше', 'меньше', 'if', 'and', 'or',
                     'not', 'then', 'else', 'when', 'than', 'equal', 'greater', 'less'}

        variables = [v for v in variables if v.lower() not in stopwords and len(v) > 1]

        return variables

    def _extract_values(self, text: str) -> List[str]:
        """
        Извлечение значений из текста действия.
        """
        values = []

        # Ищем присваивания
        assignments = re.findall(r'=\s*([^,;]+)', text)
        values.extend([a.strip() for a in assignments])

        # Ищем числа
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        values.extend(numbers)

        # Ищем строки в кавычках
        strings = re.findall(r'["\']([^"\']+)["\']', text)
        values.extend(strings)

        return values

    def _split_conditions(self, condition: str) -> List[str]:
        """
        Разбивает условие на отдельные части.
        """
        # Разбиваем по AND, OR, И, ИЛИ
        parts = re.split(r'\s+(?:and|or|и|или)\s+', condition, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    def _is_condition_subset(self, cond1: str, cond2: str) -> bool:
        """
        Проверяет, является ли cond1 подмножеством cond2.
        """
        # Извлекаем переменные из условий
        vars1 = set(self._extract_variables(cond1))
        vars2 = set(self._extract_variables(cond2))

        # Проверяем, все ли переменные cond1 есть в cond2
        if vars1 and vars1.issubset(vars2) and len(vars1) < len(vars2):
            return True

        # Проверяем текстуальную схожесть
        if self._calculate_similarity(cond1, cond2) > 0.9:
            return True

        return False

    def _are_opposite_values(self, val1: str, val2: str) -> bool:
        """
        Проверяет, являются ли значения противоположными.
        """
        opposites = [
            ('true', 'false'),
            ('yes', 'no'),
            ('да', 'нет'),
            ('true', 'no'),
            ('yes', 'false'),
            ('1', '0'),
            ('on', 'off'),
            ('вкл', 'выкл'),
            ('включен', 'выключен'),
            ('есть', 'нет'),
            ('наличие', 'отсутствие')
        ]

        val1_low = val1.lower().strip()
        val2_low = val2.lower().strip()

        for opp1, opp2 in opposites:
            if (val1_low == opp1 and val2_low == opp2) or \
                    (val1_low == opp2 and val2_low == opp1):
                return True

        return False

    def _is_cyclic_dependency(self, rule1: Dict, rule2: Dict) -> bool:
        """
        Проверяет наличие циклической зависимости между правилами.
        """
        # Действие rule1 использует переменную, которая является условием rule2
        # И действие rule2 использует переменную, которая является условием rule1
        action_vars1 = set(self._extract_variables(rule1.get('action', '')))
        condition_vars2 = set(self._extract_variables(rule2.get('condition', '')))

        action_vars2 = set(self._extract_variables(rule2.get('action', '')))
        condition_vars1 = set(self._extract_variables(rule1.get('condition', '')))

        if action_vars1.intersection(condition_vars2) and \
                action_vars2.intersection(condition_vars1):
            return True

        return False

    def _calculate_conflict_severity(self, rule1: Dict, rule2: Dict,
                                     conflict_type: str) -> int:
        """
        Вычисляет степень серьезности конфликта (1-10).
        """
        severity = 5  # Базовая серьезность

        if conflict_type == 'contradictory_assignment':
            severity = 10  # Самый серьезный
        elif conflict_type == 'different_actions':
            severity = 8
        elif conflict_type == 'cyclic_dependency':
            severity = 7
        elif conflict_type == 'different_assignment':
            severity = 6

        # Увеличиваем серьезность если правила имеют высокий приоритет
        priority1 = rule1.get('priority', 1)
        priority2 = rule2.get('priority', 1)
        if priority1 >= 7 or priority2 >= 7:
            severity = min(10, severity + 1)

        return severity

    def _get_conflict_description(self, conflict_type: str,
                                  rule1: Dict, rule2: Dict) -> str:
        """Генерирует описание конфликта."""
        descriptions = {
            'contradictory_assignment':
                f"Правила присваивают противоположные значения одной и той же переменной",
            'different_actions':
                f"При схожих условиях правила выполняют разные действия",
            'cyclic_dependency':
                f"Правила образуют циклическую зависимость",
            'different_assignment':
                f"При схожих условиях правила присваивают разные значения одной переменной"
        }

        return descriptions.get(conflict_type, f"Обнаружен конфликт типа {conflict_type}")

    def _get_conflict_recommendation(self, conflict_type: str) -> str:
        """Генерирует рекомендацию для разрешения конфликта."""
        recommendations = {
            'contradictory_assignment':
                "Измените одно из правил так, чтобы они не присваивали противоположные значения "
                "одной переменной. Возможно, одно из правил должно иметь более высокий приоритет.",
            'different_actions':
                "Объедините правила или уточните условия, чтобы они не пересекались. "
                "Рассмотрите возможность использования приоритетов.",
            'cyclic_dependency':
                "Пересмотрите логику правил, чтобы разорвать циклическую зависимость. "
                "Возможно, одно из правил должно быть изменено.",
            'different_assignment':
                "Уточните условия правил или сделайте их более специфичными, чтобы избежать "
                "неоднозначности при выполнении вывода."
        }

        return recommendations.get(conflict_type,
                                   "Проанализируйте конфликтующие правила и устраните неоднозначность.")

    def _get_similarity_recommendation(self, similarity_type: str,
                                       rule1: Dict, rule2: Dict) -> str:
        """Генерирует рекомендацию для схожих правил."""
        recommendations = {
            'identical':
                f"Правила практически идентичны. Рассмотрите возможность объединения в одно правило.",
            'same_condition':
                f"Правила имеют одинаковые условия, но разные действия. "
                f"Возможно, одно из правил избыточно или требует уточнения.",
            'same_action':
                f"Правила имеют одинаковые действия, но разные условия. "
                f"Рассмотрите возможность объединения условий.",
            'partial':
                f"Правила частично схожи. Проверьте, не являются ли они избыточными."
        }

        return recommendations.get(similarity_type, "Проанализируйте схожие правила на избыточность.")

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """
        Генерирует общие рекомендации на основе результатов анализа.
        """
        recommendations = []

        # Рекомендации на основе количества правил
        total_rules = results['total_rules']
        if total_rules == 0:
            recommendations.append("База знаний пуста. Добавьте правила для начала работы.")
        elif total_rules < 5:
            recommendations.append(f"База знаний содержит только {total_rules} правил. "
                                   "Рекомендуется добавить больше правил для повышения качества вывода.")
        elif total_rules > 100:
            recommendations.append(f"База знаний содержит {total_rules} правил. "
                                   "Рекомендуется провести рефакторинг и оптимизацию.")

        # Рекомендации на основе статистики приоритетов
        priority_dist = results['rule_statistics']['priority_distribution']
        if priority_dist['high'] > priority_dist['medium'] + priority_dist['low']:
            recommendations.append("Большинство правил имеют высокий приоритет. "
                                   "Рекомендуется пересмотреть распределение приоритетов.")

        # Рекомендации на основе схожих правил
        similar_count = len(results['similar_rules'])
        if similar_count > 0:
            recommendations.append(f"Обнаружено {similar_count} пар схожих правил. "
                                   "Рекомендуется провести рефакторинг для устранения избыточности.")

        # Рекомендации на основе конфликтов
        conflict_count = len(results['conflicting_rules'])
        if conflict_count > 0:
            recommendations.append(f"Обнаружено {conflict_count} конфликтных пар правил. "
                                   "Рекомендуется разрешить конфликты для обеспечения корректного вывода.")

        # Рекомендации на основе слабых правил
        weak_count = len(results['weak_rules'])
        if weak_count > 0:
            recommendations.append(f"Обнаружено {weak_count} потенциально слабых правил. "
                                   "Рекомендуется уточнить условия для повышения точности.")

        # Рекомендации на основе избыточных правил
        redundant_count = len(results['redundant_rules'])
        if redundant_count > 0:
            recommendations.append(f"Обнаружено {redundant_count} избыточных правил. "
                                   "Рекомендуется удалить или объединить их.")

        # Рекомендации на основе неиспользуемых переменных
        unused_vars = results['variable_usage'].get('unused_variables', [])
        if unused_vars:
            recommendations.append(f"Обнаружены переменные, которые объявляются, но не используются: "
                                   f"{', '.join(unused_vars[:3])}... "
                                   "Рекомендуется убрать неиспользуемые переменные.")

        # Рекомендации на основе неопределенных переменных
        undefined_vars = results['variable_usage'].get('undefined_variables', [])
        if undefined_vars:
            recommendations.append(f"Обнаружены переменные, которые используются, но не объявляются: "
                                   f"{', '.join(undefined_vars[:3])}... "
                                   "Рекомендуется объявить эти переменные в фактах.")

        # Общая рекомендация
        if not recommendations:
            recommendations.append("База знаний выглядит хорошо. Рекомендуется регулярно проводить "
                                   "анализ для поддержания качества.")

        # Добавляем рекомендацию по документации
        recommendations.append("Рекомендуется поддерживать документацию правил в актуальном состоянии.")

        return recommendations

    def generate_trace_report(self, agent_id: str) -> str:
        """
        Генерирует текстовый отчет по трассировке базы знаний агента.
        """
        results = self.analyze_agent_knowledge_base(agent_id)

        report = []
        report.append("=" * 80)
        report.append(f"ОТЧЕТ ПО ТРАССИРОВКЕ БАЗЫ ЗНАНИЙ АГЕНТА")
        report.append("=" * 80)
        report.append(f"Агент: {results['agent_name']}")
        report.append(f"ID агента: {results['agent_id']}")
        report.append(f"Дата анализа: {results['analysis_date']}")
        report.append("")

        # Общая статистика
        report.append("ОБЩАЯ СТАТИСТИКА")
        report.append("-" * 40)
        report.append(f"Всего правил: {results['total_rules']}")
        report.append(f"Всего фактов: {results['total_facts']}")
        report.append("")

        # Статистика правил
        stats = results['rule_statistics']
        report.append("СТАТИСТИКА ПРАВИЛ")
        report.append("-" * 40)
        report.append(f"Типы правил:")
        for rule_type, count in stats['by_type'].items():
            report.append(f"  • {rule_type}: {count}")
        report.append(f"Средний приоритет: {stats['avg_priority']}")
        report.append(f"Диапазон приоритетов: {stats['min_priority']} - {stats['max_priority']}")
        report.append(f"Распределение приоритетов:")
        report.append(f"  • Низкий (1-3): {stats['priority_distribution']['low']}")
        report.append(f"  • Средний (4-7): {stats['priority_distribution']['medium']}")
        report.append(f"  • Высокий (8-10): {stats['priority_distribution']['high']}")
        report.append("")

        # Схожие правила
        if results['similar_rules']:
            report.append("СХОЖИЕ ПРАВИЛА")
            report.append("-" * 40)
            for i, pair in enumerate(results['similar_rules'][:10], 1):
                report.append(f"{i}. Тип схожести: {pair['similarity_type']}")
                report.append(f"   Схожесть условий: {pair['condition_similarity']:.2%}")
                report.append(f"   Схожесть действий: {pair['action_similarity']:.2%}")
                report.append(f"   Правило 1: {pair['rule1'].get('name', 'Без названия')}")
                report.append(f"   Правило 2: {pair['rule2'].get('name', 'Без названия')}")
                report.append(f"   Рекомендация: {pair['recommendation']}")
                report.append("")
            if len(results['similar_rules']) > 10:
                report.append(f"... и еще {len(results['similar_rules']) - 10} пар")
                report.append("")

        # Конфликтные правила
        if results['conflicting_rules']:
            report.append("КОНФЛИКТНЫЕ ПРАВИЛА")
            report.append("-" * 40)
            for i, conflict in enumerate(results['conflicting_rules'][:10], 1):
                report.append(f"{i}. Тип конфликта: {conflict['conflict_type']}")
                report.append(f"   Серьезность: {conflict['severity']}/10")
                report.append(f"   Схожесть условий: {conflict['condition_similarity']:.2%}")
                report.append(f"   Правило 1: {conflict['rule1'].get('name', 'Без названия')}")
                report.append(f"   Правило 2: {conflict['rule2'].get('name', 'Без названия')}")
                report.append(f"   Описание: {conflict['description']}")
                report.append(f"   Рекомендация: {conflict['recommendation']}")
                report.append("")
            if len(results['conflicting_rules']) > 10:
                report.append(f"... и еще {len(results['conflicting_rules']) - 10} конфликтов")
                report.append("")

        # Избыточные правила
        if results['redundant_rules']:
            report.append("ИЗБЫТОЧНЫЕ ПРАВИЛА")
            report.append("-" * 40)
            for i, redundant in enumerate(results['redundant_rules'][:5], 1):
                report.append(f"{i}. Избыточное правило: {redundant['redundant_rule'].get('name', 'Без названия')}")
                report.append(f"   Базовое правило: {redundant['superset_rule'].get('name', 'Без названия')}")
                report.append(f"   Причина: {redundant['reason']}")
                report.append(f"   Рекомендация: {redundant['recommendation']}")
                report.append("")
            if len(results['redundant_rules']) > 5:
                report.append(f"... и еще {len(results['redundant_rules']) - 5} избыточных правил")
                report.append("")

        # Слабые правила
        if results['weak_rules']:
            report.append("СЛАБЫЕ ПРАВИЛА")
            report.append("-" * 40)
            for i, weak in enumerate(results['weak_rules'][:5], 1):
                report.append(f"{i}. Правило: {weak['rule'].get('name', 'Без названия')}")
                report.append(f"   Проблема: {weak['description']}")
                report.append(f"   Рекомендация: {weak['recommendation']}")
                report.append("")
            if len(results['weak_rules']) > 5:
                report.append(f"... и еще {len(results['weak_rules']) - 5} слабых правил")
                report.append("")

        # Цепочки правил
        if results['rule_chains']:
            report.append("ЦЕПОЧКИ ПРАВИЛ")
            report.append("-" * 40)
            for i, chain in enumerate(results['rule_chains'][:5], 1):
                report.append(f"{i}. {chain['description']}")
                report.append("")
            if len(results['rule_chains']) > 5:
                report.append(f"... и еще {len(results['rule_chains']) - 5} цепочек")
                report.append("")

        # Переменные
        var_usage = results['variable_usage']
        if var_usage['variables']:
            report.append("ИСПОЛЬЗОВАНИЕ ПЕРЕМЕННЫХ")
            report.append("-" * 40)
            # Показываем топ-10 переменных
            sorted_vars = sorted(var_usage['variables'].items(),
                                 key=lambda x: x[1]['in_conditions'] + x[1]['in_actions'],
                                 reverse=True)
            for var, usage in sorted_vars[:10]:
                report.append(f"  • {var}: условий - {usage['in_conditions']}, действий - {usage['in_actions']}")
            if len(sorted_vars) > 10:
                report.append(f"  ... и еще {len(sorted_vars) - 10} переменных")
            report.append("")

        if var_usage['unused_variables']:
            report.append(f"Неиспользуемые переменные: {', '.join(var_usage['unused_variables'][:5])}")
            report.append("")

        if var_usage['undefined_variables']:
            report.append(f"Неопределенные переменные: {', '.join(var_usage['undefined_variables'][:5])}")
            report.append("")

        # Рекомендации
        report.append("Рекомендации")
        report.append("-" * 40)
        for i, rec in enumerate(results['recommendations'], 1):
            report.append(f"{i}. {rec}")
        report.append("")

        report.append("=" * 80)
        report.append("Конец отчета")
        report.append("=" * 80)

        return "\n".join(report)