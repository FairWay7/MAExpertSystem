"""Методы прямого и обратного вывода"""

import re
from typing import List, Dict, Optional
from PyQt5.QtWidgets import *


def forward_inference_impl(self):
    """Прямой вывод"""
    if not self.current_agent_id:
        QMessageBox.warning(self, "Ошибка", "Сначала выберите агента")
        return

    dialog = QDialog(self)
    dialog.setWindowTitle("Прямой вывод")
    dialog.setMinimumWidth(500)

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Введите начальные факты (каждый с новой строки):"))

    facts_edit = QTextEdit()
    facts_edit.setPlaceholderText("температура = 39.5\nдавление = 150/95")
    layout.addWidget(facts_edit)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        facts_text = facts_edit.toPlainText()
        initial_facts = []

        for line in facts_text.split('\n'):
            line = line.strip()
            if line:
                parts = line.split('=')
                if len(parts) == 2:
                    initial_facts.append({
                        'variable': parts[0].strip(),
                        'value': parts[1].strip()
                    })

        rules = self.db_manager.get_rules_by_agent(self.current_agent_id)

        self.explanation.clear()
        self.explanation.start_trace("прямой")

        result = simple_forward_chaining_impl(self, initial_facts, rules)
        report = create_inference_report_impl("Прямой вывод", initial_facts, rules, result)
        trace_report = self.explanation.get_full_trace()
        full_report = report + "\n\n" + trace_report

        self.trace_text.setText(full_report)
        self.explanation_text.setText(trace_report)
        self.tab_widget.setCurrentIndex(4)
        self.statusBar().showMessage("Прямой вывод выполнен")


def simple_forward_chaining_impl(self, initial_facts: List, rules: List) -> Dict:
    """Простой алгоритм прямого вывода"""
    working_memory = {}
    for fact in initial_facts:
        # Преобразуем значение в правильный тип
        value = fact['value']
        if value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        elif value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        # Иначе оставляем как строку
        working_memory[fact['variable']] = value
        self.explanation.add_fact_inferred(fact['variable'], value,
                                           {'name': 'начальный факт'})

    applied_rules = []
    new_facts = []
    sorted_rules = sorted(rules, key=lambda x: x.get('priority', 1), reverse=True)

    changed = True
    iteration = 0
    while changed and iteration < 100:
        changed = False
        iteration += 1
        self.explanation.add_step("ITERATION", f"Итерация {iteration}")

        for rule in sorted_rules:
            condition_result = check_rule_condition_impl(rule['condition'], working_memory)
            self.explanation.add_condition_check(rule['condition'], condition_result, working_memory)

            if condition_result:
                action_result = execute_rule_action_impl(rule['action'], working_memory)

                if action_result:
                    variable, value = action_result

                    if variable not in working_memory:
                        working_memory[variable] = value
                        new_facts.append({
                            'variable': variable,
                            'value': value,
                            'rule': rule.get('name', rule['condition'])
                        })
                        applied_rules.append(rule.get('name', rule['condition']))
                        self.explanation.add_rule_fire(rule, working_memory, action_result)
                        changed = True

    return {
        'final_facts': working_memory,
        'applied_rules': applied_rules,
        'new_facts': new_facts,
        'iterations': iteration
    }


def check_rule_condition_impl(condition: str, facts: Dict) -> bool:
    """
    Проверка условия правила с улучшенной обработкой строк и чисел.

    Поддерживает:
    - Сравнение чисел: температура > 38.0
    - Сравнение строк: гипертония = "да" или гипертония = да
    - Логические операторы: и, или, and, or
    - Сравнения: >, <, >=, <=, =, ==, !=
    """
    try:
        # Создаем копию фактов для безопасного изменения
        local_facts = facts.copy()

        # Нормализуем условие: заменяем русские операторы на английские
        expr = condition
        expr = expr.replace('и', ' and ').replace('или', ' or ')

        # Обрабатываем каждый факт
        for var, value in local_facts.items():
            # Преобразуем значение в правильный формат
            formatted_value = _format_value_for_eval(value)

            # Заменяем переменную на отформатированное значение
            # Используем границы слова для точной замены
            pattern = r'\b' + re.escape(var) + r'\b'
            expr = re.sub(pattern, formatted_value, expr)

        # Если в выражении остались незамененные переменные, пробуем их найти в facts
        # и подставить значения
        for var, value in local_facts.items():
            if var in expr:
                formatted_value = _format_value_for_eval(value)
                expr = expr.replace(var, formatted_value)

        # Вычисляем выражение
        result = eval(expr)
        return bool(result)

    except Exception as e:
        # Если eval не сработал, пробуем альтернативный метод
        try:
            return _check_condition_fallback(condition, local_facts)
        except:
            return False


def _format_value_for_eval(value: any) -> str:
    """Форматирует значение для использования в eval()"""
    if isinstance(value, str):
        # Убираем лишние кавычки, если они есть
        cleaned = value.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        if cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1]
        # Добавляем кавычки для строк
        return f'"{cleaned}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return f'"{str(value)}"'


def _check_condition_fallback(condition: str, facts: Dict) -> bool:
    """
    Альтернативный метод проверки условий без использования eval()
    """
    # Разбиваем условие на части по логическим операторам
    parts = re.split(r'\s+(?:and|or|и|или)\s+', condition, flags=re.IGNORECASE)

    # Определяем, какой оператор используется (and или or)
    if ' or ' in condition.lower() or 'или' in condition.lower():
        operator = 'or'
    else:
        operator = 'and'

    results = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Проверяем один атомарный блок условия
        result = _check_single_condition(part, facts)
        results.append(result)

    if operator == 'and':
        return all(results)
    else:
        return any(results)


def _check_single_condition(condition: str, facts: Dict) -> bool:
    """
    Проверяет одно атомарное условие (без логических операторов)
    """
    condition = condition.strip()

    # Ищем операторы сравнения
    # Проверяем наличие >=, <=, >, <, =, !=
    operators = ['>=', '<=', '!=', '=', '>', '<']

    for op in operators:
        if op in condition:
            parts = condition.split(op, 1)
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()

                # Получаем значения левой и правой части
                left_value = _get_value_from_facts(left, facts)
                right_value = _get_value_from_facts(right, facts)

                # Сравниваем в зависимости от оператора
                return _compare_values(left_value, right_value, op)

    # Если нет оператора, проверяем на наличие переменной в фактах
    # (например, просто "гипертония")
    if condition in facts:
        return bool(facts[condition])

    return False


def _get_value_from_facts(expression: str, facts: Dict):
    """
    Получает значение из фактов или парсит литерал
    """
    expression = expression.strip()

    # Если это число
    try:
        if '.' in expression:
            return float(expression)
        else:
            return int(expression)
    except ValueError:
        pass

    # Если это булево значение
    if expression.lower() in ('true', 'false'):
        return expression.lower() == 'true'

    # Если это строка в кавычках
    if (expression.startswith('"') and expression.endswith('"')) or \
            (expression.startswith("'") and expression.endswith("'")):
        return expression[1:-1]

    # Если это переменная из фактов
    if expression in facts:
        return facts[expression]

    # Иначе возвращаем как строку
    return expression


def _compare_values(left, right, operator: str) -> bool:
    """
    Сравнивает два значения с заданным оператором
    """
    try:
        if operator == '=' or operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '>':
            return float(left) > float(right)
        elif operator == '<':
            return float(left) < float(right)
        elif operator == '>=':
            return float(left) >= float(right)
        elif operator == '<=':
            return float(left) <= float(right)
    except (ValueError, TypeError):
        # Если не удалось преобразовать к числам, сравниваем как строки
        left_str = str(left).lower()
        right_str = str(right).lower()

        if operator == '=' or operator == '==':
            return left_str == right_str
        elif operator == '!=':
            return left_str != right_str
        else:
            # Для >, < со строками используем лексикографическое сравнение
            return False

    return False


def execute_rule_action_impl(action: str, facts: Dict) -> Optional[tuple]:
    """
    Выполнение действия правила с улучшенной обработкой присваиваний
    """
    # Ищем паттерн присваивания: переменная = значение
    patterns = [
        r'([\wа-яА-Я_]+)\s*=\s*"([^"]*)"',  # переменная = "значение"
        r'([\wа-яА-Я_]+)\s*=\s*\'([^\']*)\'',  # переменная = 'значение'
        r'([\wа-яА-Я_]+)\s*=\s*([\d.]+)',  # переменная = 123.45
        r'([\wа-яА-Я_]+)\s*=\s*(true|false)',  # переменная = true/false
        r'([\wа-яА-Я_]+)\s*=\s*([^,;\n]+)',  # переменная = значение (общий случай)
    ]

    for pattern in patterns:
        match = re.match(pattern, action, re.IGNORECASE)
        if match:
            variable = match.group(1).strip()
            value = match.group(2).strip()

            # Пытаемся определить тип значения
            # Если это число с плавающей точкой
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Если это булево значение
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Иначе оставляем как строку (без кавычек)
                else:
                    # Убираем кавычки, если они есть
                    if (value.startswith('"') and value.endswith('"')) or \
                            (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

            return (variable, value)

    return None


def create_inference_report_impl(inference_type: str, initial_facts: List,
                                 rules: List, result: Dict) -> str:
    """Создание отчета о выводе"""
    report = "=" * 80 + "\n"
    report += f"ОТЧЕТ О ВЫВОДЕ: {inference_type}\n"
    report += "=" * 80 + "\n\n"

    report += "НАЧАЛЬНЫЕ ФАКТЫ:\n"
    for fact in initial_facts:
        report += f"  • {fact['variable']} = {fact['value']}\n"

    report += f"\nВСЕГО ПРАВИЛ: {len(rules)}\n"
    report += f"ИТЕРАЦИЙ: {result.get('iterations', 0)}\n\n"

    if result['applied_rules']:
        report += "ПРИМЕНЕННЫЕ ПРАВИЛА:\n"
        for i, rule_name in enumerate(result['applied_rules'], 1):
            report += f"  {i}. {rule_name}\n"

    if result['new_facts']:
        report += "\nНОВЫЕ ФАКТЫ:\n"
        for fact in result['new_facts']:
            report += f"  • {fact['variable']} = {fact['value']} "
            report += f"(из правила: {fact['rule']})\n"

    report += "\nИТОГОВАЯ РАБОЧАЯ ПАМЯТЬ:\n"
    for var, value in result['final_facts'].items():
        report += f"  • {var} = {value}\n"

    report += "\n" + "=" * 80
    return report


def backward_inference_impl(self):
    """Обратный вывод"""
    if not self.current_agent_id:
        QMessageBox.warning(self, "Ошибка", "Сначала выберите агента")
        return

    goal, ok = QInputDialog.getText(
        self, "Обратный вывод",
        "Введите цель для доказательства (например, 'диагноз'):"
    )

    if ok and goal:
        self.explanation.clear()
        self.explanation.start_trace("обратный", goal)

        report = create_backward_inference_report_impl(self, goal)
        trace_report = self.explanation.get_full_trace()
        full_report = report + "\n\n" + trace_report

        self.trace_text.setText(full_report)
        self.explanation_text.setText(trace_report)
        self.tab_widget.setCurrentIndex(4)
        self.statusBar().showMessage(f"Обратный вывод для цели: {goal}")


def create_backward_inference_report_impl(self, goal: str) -> str:
    """Создание отчета обратного вывода"""
    report = "=" * 80 + "\n"
    report += f"ОБРАТНЫЙ ВЫВОД: доказать '{goal}'\n"
    report += "=" * 80 + "\n\n"

    rules = self.db_manager.get_rules_by_agent(self.current_agent_id)

    relevant_rules = []
    for rule in rules:
        if goal.lower() in rule['action'].lower():
            relevant_rules.append(rule)
            self.explanation.add_step("RULE_FOUND",
                                      f"Найдено правило, выводящее '{goal}': {rule.get('name', rule['condition'])}")

    if not relevant_rules:
        report += f"Не найдено правил, выводящих '{goal}'\n"
        self.explanation.add_goal_proven(goal, False)
    else:
        report += f"Найдено правил, выводящих '{goal}': {len(relevant_rules)}\n\n"

        for i, rule in enumerate(relevant_rules, 1):
            report += f"ПРАВИЛО {i}:\n"
            report += f"  ЕСЛИ: {rule['condition']}\n"
            report += f"  ТО: {rule['action']}\n"
            report += f"  Приоритет: {rule.get('priority', 1)}\n\n"

            conditions = extract_conditions_impl(self, rule['condition'])
            report += f"  Условия для доказательства:\n"
            for cond in conditions:
                report += f"    • {cond}\n"
            report += "\n"

    report += "\n" + "=" * 80
    return report


def extract_conditions_impl(self, condition_text: str) -> List[str]:
    """Извлечение условий из текста условия"""
    import re
    conditions = []
    parts = re.split(r'\s+и\s+|\s+или\s+', condition_text, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if part:
            conditions.append(part)
            self.explanation.add_step("CONDITION_EXTRACT", f"Извлечено условие: {part}")

    return conditions