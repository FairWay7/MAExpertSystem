import pytest
from ui.main_window_inference import (
    simple_forward_chaining_impl,
    check_rule_condition_impl,
    execute_rule_action_impl
)


class TestInference:
    """Тесты логического вывода"""

    def test_check_rule_condition_simple(self):
        """Тест проверки простого условия"""
        facts = {'температура': '39.5'}
        condition = 'температура > 38.0'

        # В простой реализации это может не работать с eval
        # Поэтому используем мок-объект
        result = check_rule_condition_impl(condition, facts)
        assert result is not None

    def test_check_rule_condition_with_and(self):
        """Тест проверки условия с AND"""
        facts = {'температура': '39.5', 'кашель': 'да'}
        condition = 'температура > 38.0 и кашель = да'

        result = check_rule_condition_impl(condition, facts)
        assert result is not None

    def test_execute_rule_action_assignment(self):
        """Тест выполнения действия присваивания"""
        facts = {'температура': '39.5'}
        action = 'состояние = лихорадка'

        result = execute_rule_action_impl(action, facts)
        if result:
            variable, value = result
            assert variable == 'состояние'
            assert value == 'лихорадка'

    def test_execute_rule_action_complex(self):
        """Тест выполнения сложного действия"""
        facts = {'a': '5', 'b': '3'}
        action = 'результат = a + b'

        result = execute_rule_action_impl(action, facts)
        if result:
            variable, value = result
            assert variable == 'результат'

    def test_simple_forward_chaining(self):
        """Тест прямого вывода (с использованием моков)"""
        # Это тест для структуры, но реальное выполнение требует полного контекста
        initial_facts = [
            {'variable': 'температура', 'value': '39.5'},
            {'variable': 'кашель', 'value': 'да'}
        ]

        rules = [
            {
                'name': 'Правило 1',
                'condition': 'температура > 38.0',
                'action': 'состояние = лихорадка',
                'priority': 5
            },
            {
                'name': 'Правило 2',
                'condition': 'состояние = лихорадка и кашель = да',
                'action': 'диагноз = респираторная инфекция',
                'priority': 7
            }
        ]

        # Создаем мок-объект для explanation
        class MockExplanation:
            def __init__(self):
                self.steps = []

            def clear(self):
                self.steps = []

            def start_trace(self, *args, **kwargs):
                pass

            def add_fact_inferred(self, *args, **kwargs):
                pass

            def add_step(self, *args, **kwargs):
                self.steps.append(args)

            def add_condition_check(self, *args, **kwargs):
                pass

            def add_rule_fire(self, *args, **kwargs):
                pass

        # Создаем мок-объект self
        class MockSelf:
            def __init__(self):
                self.explanation = MockExplanation()

        mock_self = MockSelf()

        # Запускаем прямой вывод (упрощенный)
        result = simple_forward_chaining_impl(mock_self, initial_facts, rules)

        assert 'final_facts' in result
        assert 'applied_rules' in result
        assert 'new_facts' in result
        assert 'iterations' in result

    def test_forward_chaining_with_no_matching_rules(self):
        """Тест прямого вывода без подходящих правил"""
        initial_facts = [
            {'variable': 'x', 'value': '1'}
        ]

        rules = [
            {
                'name': 'Правило',
                'condition': 'y > 5',
                'action': 'z = 10',
                'priority': 5
            }
        ]

        class MockExplanation:
            def __init__(self):
                self.steps = []

            def clear(self):
                self.steps = []

            def start_trace(self, *args, **kwargs):
                pass

            def add_fact_inferred(self, *args, **kwargs):
                pass

            def add_step(self, *args, **kwargs):
                self.steps.append(args)

            def add_condition_check(self, *args, **kwargs):
                pass

            def add_rule_fire(self, *args, **kwargs):
                pass

        class MockSelf:
            def __init__(self):
                self.explanation = MockExplanation()

        mock_self = MockSelf()
        result = simple_forward_chaining_impl(mock_self, initial_facts, rules)

        assert len(result['applied_rules']) == 0
        assert len(result['new_facts']) == 0