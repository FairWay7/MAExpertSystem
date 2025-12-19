from typing import List, Dict, Any, Tuple
from models.rule import Rule
from models.fact import Fact
import re


class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.explanation_steps = []

    def forward_chaining(self, initial_facts: List[Fact] = None) -> List[Dict]:
        """Прямой вывод"""
        self.explanation_steps = []
        working_memory = initial_facts or []

        # Добавляем начальные факты
        for fact in working_memory:
            self.log_step(f"Исходный факт: {fact.variable_name} = {fact.value}")

        new_facts_added = True
        iteration = 0

        while new_facts_added and iteration < 100:  # Защита от бесконечного цикла
            new_facts_added = False
            iteration += 1

            for rule in sorted(self.kb.rules.values(), key=lambda x: x.priority, reverse=True):
                if self.check_condition(rule.condition, working_memory):
                    # Правило сработало
                    new_fact = self._execute_action(rule.action, rule.agent_id)
                    if new_fact and not self._fact_exists(new_fact, working_memory):
                        working_memory.append(new_fact)
                        new_facts_added = True

                        self.log_step(f"Сработало правило: {rule.name}")
                        self.log_step(f"  Условие: {rule.condition}")
                        self.log_step(f"  Действие: {rule.action}")
                        self.log_step(f"  Новый факт: {new_fact.variable_name} = {new_fact.value}")

        return working_memory

    def backward_chaining(self, goal: str, working_memory: List[Fact] = None) -> Tuple[bool, List]:
        """Обратный вывод"""
        self.explanation_steps = []
        working_memory = working_memory or []

        self.log_step(f"Цель: доказать {goal}")
        result = self._prove_goal(goal, working_memory, [])

        return result

    # Попытка доказать цель
    def _prove_goal(self, goal: str, working_memory: List[Fact], visited: List) -> Tuple[bool, List]:
        # Проверяем, есть ли факт в рабочей памяти
        for fact in working_memory:
            if fact.variable_name == goal:
                self.log_step(f"Цель '{goal}' найдена в фактах: {fact.value}")
                return True, working_memory

        # Ищем правила, которые могут вывести цель
        relevant_rules = []
        for rule in self.kb.rules.values():
            if self._extract_conclusion(rule.action) == goal:
                relevant_rules.append(rule)

        if not relevant_rules:
            self.log_step(f"Нет правил для вывода цели '{goal}'")
            return False, working_memory

        # Пробуем каждое правило
        for rule in relevant_rules:
            self.log_step(f"Пробуем правило: {rule.name}")
            self.log_step(f"  Действие: {rule.action}")

            # Проверяем условия правила
            conditions = self._extract_conditions(rule.condition)
            all_conditions_met = True

            for condition in conditions:
                cond_result, _ = self._prove_goal(condition, working_memory, visited + [goal])
                if not cond_result:
                    all_conditions_met = False
                    break

            if all_conditions_met:
                # Все условия выполнены, выполняем действие
                new_fact = self._execute_action(rule.action, rule.agent_id)
                working_memory.append(new_fact)
                self.log_step(f"Правило успешно применено, получен факт: {new_fact.variable_name} = {new_fact.value}")
                return True, working_memory

        return False, working_memory

    def check_condition(self, condition: str, facts: List[Fact]) -> bool:
        """Проверка условия правила"""
        # Простая реализация - можно расширить
        try:
            return eval(condition, {}, {f.variable_name: f.value for f in facts})
        except:
            return False

    def log_step(self, message: str):
        """Запись шага вывода"""
        self.explanation_steps.append(message)