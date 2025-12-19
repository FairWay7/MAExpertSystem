import uuid
from datetime import datetime

test_rules = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Правило температуры',
            'condition': 'температура > 38',
            'action': 'диагноз = "лихорадка"',
            'agent': 'expert1',
            'priority': 1,
            'author': 'Система',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Правило давления',
            'condition': 'давление > 140/90',
            'action': 'диагноз = "гипертония"',
            'agent': 'expert1',
            'priority': 2,
            'author': 'Система',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Правило двигателя',
            'condition': 'температура_двигателя > 100',
            'action': 'статус = "перегрев"',
            'agent': 'expert2',
            'priority': 1,
            'author': 'Система',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    ]