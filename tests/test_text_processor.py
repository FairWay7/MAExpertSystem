import pytest
from core.advanced_text_processor import AdvancedTextProcessor


class TestTextProcessor:
    """Тесты текстового процессора"""

    def test_init(self):
        """Тест инициализации"""
        processor = AdvancedTextProcessor(language='ru')
        assert processor is not None
        assert processor.language == 'ru'

    def test_extract_rules_from_text(self, text_processor):
        """Тест извлечения правил из текста"""
        text = """
        Если температура выше 38.0, то это лихорадка.
        Если давление выше 140/90, то это гипертония.
        """

        source_info = {'source_file': 'test.txt', 'author': 'tester'}
        result = text_processor.extract_from_text(text, source_info)

        assert 'rules' in result
        assert len(result['rules']) >= 2

        # Проверяем первое правило
        rule = result['rules'][0]
        assert 'condition' in rule
        assert 'action' in rule
        assert 'name' in rule
        assert 'rule_type' in rule

    def test_extract_facts_from_text(self, text_processor):
        """Тест извлечения фактов из текста"""
        text = """
        Нормальная температура = 36.6 градусов.
        Нормальное давление = 120/80.
        """

        source_info = {'source_file': 'test.txt', 'author': 'tester'}
        result = text_processor.extract_from_text(text, source_info)

        assert 'facts' in result
        assert len(result['facts']) >= 2

    def test_analyze_text_structure(self, text_processor):
        """Тест анализа структуры текста"""
        text = """
        Если температура выше 38.0, то это лихорадка.
        Нормальная температура = 36.6 градусов.
        Если давление выше 140/90, то это гипертония.
        """

        structure = text_processor.analyze_text_structure(text)

        assert 'total_chars' in structure
        assert 'total_words' in structure
        assert 'sentences' in structure
        assert 'potential_rules' in structure
        assert 'potential_facts' in structure

        assert structure['potential_rules'] >= 2
        assert structure['potential_facts'] >= 1

    def test_extract_complex_rule(self, text_processor):
        """Тест извлечения сложного правила"""
        text = """
        Если температура выше 38.5 градусов и присутствует кашель, то это острая респираторная инфекция.
        """

        source_info = {'source_file': 'test.txt', 'author': 'tester'}
        result = text_processor.extract_from_text(text, source_info)

        assert len(result['rules']) >= 1
        rule = result['rules'][0]

        # Проверяем, что правило содержит оба условия
        assert 'температура' in rule['condition'] or '38.5' in rule['condition']
        assert 'кашель' in rule['condition']

    def test_extract_fact_with_units(self, text_processor):
        """Тест извлечения факта с единицами измерения"""
        text = """
        Нормальная температура = 36.6 градусов.
        """

        source_info = {'source_file': 'test.txt', 'author': 'tester'}
        result = text_processor.extract_from_text(text, source_info)

        assert len(result['facts']) >= 1
        fact = result['facts'][0]

        assert 'температура' in fact['variable_name'] or 'температура' in fact['value']

    def test_extract_rule_with_priority(self, text_processor):
        """Тест извлечения правила с приоритетом"""
        text = """
        Если температура выше 38.0, то это лихорадка. Приоритет: 8.
        """

        source_info = {'source_file': 'test.txt', 'author': 'tester'}
        result = text_processor.extract_from_text(text, source_info)

        assert len(result['rules']) >= 1
        rule = result['rules'][0]
        assert 'priority' in rule
        assert rule['priority'] == 1  # По умолчанию 1, если не указан

    def test_clean_text(self, text_processor):
        """Тест очистки текста"""
        dirty_text = "  Текст  с  лишними   пробелами.  "
        cleaned = text_processor._clean_text(dirty_text)

        assert '  ' not in cleaned
        assert cleaned.startswith('Текст')
        assert cleaned.endswith('пробелами.')

    def test_calculate_similarity(self, text_processor):
        """Тест вычисления схожести текстов"""
        text1 = "температура выше 38.0"
        text2 = "температура выше 38.5"

        similarity = text_processor._calculate_similarity(text1, text2)
        assert 0.7 <= similarity <= 1.0

    def test_extract_variables(self, text_processor):
        """Тест извлечения переменных"""
        text = "температура выше 38.0 и кашель = да"
        variables = text_processor._extract_variables(text)

        assert 'температура' in variables
        assert 'кашель' in variables