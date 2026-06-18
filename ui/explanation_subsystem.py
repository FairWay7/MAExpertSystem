from typing import List

from PyQt5.QtCore import QDateTime


class ExplanationSubsystem:
    """Подсистема объяснения вывода"""

    def __init__(self):
        self.trace_steps = []

    def start_trace(self, inference_type: str, goal: str = None):
        """Начало трассировки"""
        self.trace_steps = []
        self.add_step("START", f"Начало {inference_type} вывода" +
                      (f" с целью: {goal}" if goal else ""))

    def add_step(self, step_type: str, description: str, data: dict = None):
        """Добавление шага в трассировку"""
        step = {
            'number': len(self.trace_steps) + 1,
            'type': step_type,
            'description': description,
            'data': data or {},
            'timestamp': QDateTime.currentDateTime().toString("HH:mm:ss")
        }
        self.trace_steps.append(step)

    def add_rule_fire(self, rule: dict, facts: dict, result: any):
        """Добавление срабатывания правила"""
        self.add_step("RULE_FIRE",
                      f"Правило '{rule.get('name', 'unknown')}' сработало",
                      {'rule': rule, 'facts': facts, 'result': result})

    def add_condition_check(self, condition: str, result: bool, facts: dict):
        """Добавление проверки условия"""
        self.add_step("CONDITION",
                      f"Проверка условия: {condition} = {result}",
                      {'condition': condition, 'result': result, 'facts': facts})

    def add_fact_inferred(self, variable: str, value: any, rule: dict):
        """Добавление выведенного факта"""
        self.add_step("FACT_INFERRED",
                      f"Выведен факт: {variable} = {value}",
                      {'variable': variable, 'value': value, 'rule': rule})

    def add_goal_proven(self, goal: str, success: bool):
        """Добавление результата доказательства цели"""
        self.add_step("GOAL",
                      f"Цель '{goal}' {'доказана' if success else 'не доказана'}",
                      {'goal': goal, 'success': success})

    def get_full_trace(self) -> str:
        """Получение полной трассировки"""
        if not self.trace_steps:
            return "Нет данных трассировки"

        trace_text = "=" * 80 + "\n"
        trace_text += "ТРАССИРОВКА ВЫВОДА\n"
        trace_text += "=" * 80 + "\n\n"

        for step in self.trace_steps:
            trace_text += f"[{step['timestamp']}] Шаг {step['number']}: {step['description']}\n"
            if step['data']:
                trace_text += f"    Данные: {step['data']}\n"
            trace_text += "\n"

        trace_text += "=" * 80
        return trace_text

    def get_step_by_step(self) -> List[str]:
        """Получение пошагового объяснения"""
        return [f"Шаг {step['number']}: {step['description']}" for step in self.trace_steps]

    def clear(self):
        """Очистка трассировки"""
        self.trace_steps = []