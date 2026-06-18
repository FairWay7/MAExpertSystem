import pytest
from core.trace_analyzer import TraceAnalyzer


class TestTraceAnalyzer:
    """Тесты анализатора трассировки"""

    def test_analyze_empty_knowledge_base(self, trace_analyzer, sample_agent):
        """Тест анализа пустой базы знаний"""
        result = trace_analyzer.analyze_agent_knowledge_base(sample_agent['id'])

        assert result['agent_id'] == sample_agent['id']
        assert result['total_rules'] == 0
        assert result['total_facts'] == 0
        assert 'recommendations' in result
        assert 'Пуста' in result['recommendations'][0] or 'нет правил' in result['recommendations'][0]

    def test_analyze_with_rules(self, trace_analyzer, temp_db, sample_agent):
        """Тест анализа с правилами"""
        # Добавляем правила
        rules = [
            {
                'name': 'Правило 1',
                'condition': 'температура > 38.0',
                'action': 'состояние = лихорадка',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            },
            {
                'name': 'Правило 2',
                'condition': 'состояние = лихорадка и кашель = да',
                'action': 'диагноз = респираторная инфекция',
                'rule_type': 'conditional',
                'priority': 7,
                'agent_id': sample_agent['id']
            }
        ]

        for rule_data in rules:
            temp_db.save_rule(rule_data)

        result = trace_analyzer.analyze_agent_knowledge_base(sample_agent['id'])

        assert result['total_rules'] == 2
        assert result['rule_statistics']['total'] == 2
        assert 'conditional' in result['rule_statistics']['by_type']

    def test_find_similar_rules(self, trace_analyzer, temp_db, sample_agent):
        """Тест поиска схожих правил"""
        rules = [
            {
                'name': 'Правило 1',
                'condition': 'температура > 38.0',
                'action': 'состояние = лихорадка',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            },
            {
                'name': 'Правило 2',
                'condition': 'температура > 38.5',
                'action': 'состояние = сильная лихорадка',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            }
        ]

        for rule_data in rules:
            temp_db.save_rule(rule_data)

        result = trace_analyzer.analyze_agent_knowledge_base(sample_agent['id'])

        # Должны быть найдены схожие правила
        assert len(result['similar_rules']) >= 1

    def test_find_conflicting_rules(self, trace_analyzer, temp_db, sample_agent):
        """Тест поиска конфликтных правил"""
        rules = [
            {
                'name': 'Правило 1',
                'condition': 'температура > 38.0',
                'action': 'состояние = здоров',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            },
            {
                'name': 'Правило 2',
                'condition': 'температура > 38.0',
                'action': 'состояние = болен',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            }
        ]

        for rule_data in rules:
            temp_db.save_rule(rule_data)

        result = trace_analyzer.analyze_agent_knowledge_base(sample_agent['id'])

        # Должны быть найдены конфликтные правила
        assert len(result['conflicting_rules']) >= 1

    def test_find_weak_rules(self, trace_analyzer, temp_db, sample_agent):
        """Тест поиска слабых правил"""
        rules = [
            {
                'name': 'Слишком простое правило',
                'condition': 'температура > 38.0',
                'action': 'состояние = лихорадка',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            },
            {
                'name': 'Сложное правило',
                'condition': 'a > b and c < d and e = f and g > h and i = j and k > l',
                'action': 'результат = true',
                'rule_type': 'conditional',
                'priority': 5,
                'agent_id': sample_agent['id']
            }
        ]

        for rule_data in rules:
            temp_db.save_rule(rule_data)

        result = trace_analyzer.analyze_agent_knowledge_base(sample_agent['id'])

        # Должны быть найдены слабые правила
        assert len(result['weak_rules']) >= 2

    def test_generate_trace_report(self, trace_analyzer, temp_db, sample_agent):
        """Тест генерации отчета трассировки"""
        # Добавляем правило
        rule_data = {
            'name': 'Тестовое правило',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5,
            'agent_id': sample_agent['id']
        }
        temp_db.save_rule(rule_data)

        report = trace_analyzer.generate_trace_report(sample_agent['id'])

        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0
        assert 'ОТЧЕТ ПО ТРАССИРОВКЕ' in report or 'ТРАССИРОВКИ' in report

    def test_calculate_similarity(self, trace_analyzer):
        """Тест вычисления схожести"""
        text1 = "температура выше 38.0"
        text2 = "температура выше 38.5"

        similarity = trace_analyzer._calculate_similarity(text1, text2)
        assert 0.0 <= similarity <= 1.0

    def test_extract_variables(self, trace_analyzer):
        """Тест извлечения переменных"""
        text = "температура выше 38.0 и кашель = да"
        variables = trace_analyzer._extract_variables(text)

        assert 'температура' in variables
        assert 'кашель' in variables

    def test_are_opposite_values(self, trace_analyzer):
        """Тест определения противоположных значений"""
        assert trace_analyzer._are_opposite_values('true', 'false') is True
        assert trace_analyzer._are_opposite_values('да', 'нет') is True
        assert trace_analyzer._are_opposite_values('true', 'true') is False
        assert trace_analyzer._are_opposite_values('да', 'да') is False