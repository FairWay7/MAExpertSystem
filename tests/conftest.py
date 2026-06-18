import pytest
import os
import tempfile
import sqlite3
from pathlib import Path

from database.db_manager import DatabaseManager
from core.advanced_text_processor import AdvancedTextProcessor
from core.trace_analyzer import TraceAnalyzer


@pytest.fixture
def temp_db():
    """Создание временной базы данных для тестов"""
    fd, path = tempfile.mkstemp(suffix='.sqlite3')
    os.close(fd)
    db = DatabaseManager(path)
    yield db
    # Удаляем временный файл после тестов
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def text_processor():
    """Фикстура для текстового процессора"""
    return AdvancedTextProcessor(language='ru')


@pytest.fixture
def trace_analyzer(temp_db):
    """Фикстура для анализатора трассировки"""
    return TraceAnalyzer(temp_db)


@pytest.fixture
def sample_rules():
    """Набор тестовых правил"""
    return [
        {
            'name': 'Правило 1',
            'condition': 'температура > 38.0',
            'action': 'состояние = лихорадка',
            'rule_type': 'conditional',
            'priority': 5
        },
        {
            'name': 'Правило 2',
            'condition': 'состояние = лихорадка и кашель = да',
            'action': 'диагноз = респираторная инфекция',
            'rule_type': 'conditional',
            'priority': 7
        },
        {
            'name': 'Правило 3',
            'condition': 'давление > 140/90',
            'action': 'гипертония = да',
            'rule_type': 'conditional',
            'priority': 8
        }
    ]


@pytest.fixture
def sample_facts():
    """Набор тестовых фактов"""
    return [
        {
            'variable_name': 'температура',
            'value': '39.5',
            'confidence': 0.95
        },
        {
            'variable_name': 'кашель',
            'value': 'да',
            'confidence': 0.9
        },
        {
            'variable_name': 'давление',
            'value': '150/95',
            'confidence': 0.85
        }
    ]


@pytest.fixture
def sample_agent(temp_db):
    """Создание тестового агента"""
    domain = temp_db.create_domain('Тестовый домен', 'Для тестирования')
    agent = temp_db.create_agent('Тестовый агент', domain['id'], 'Тестовый агент')
    return agent


@pytest.fixture
def sample_text():
    """Тестовый текст для анализа"""
    return """
    Если температура выше 38.5 градусов и присутствует кашель, то это острая респираторная инфекция.
    Если давление выше 140/90, то это гипертония.
    Нормальная температура = 36.6 градусов.
    Нормальное давление = 120/80.
    """