import uuid
from datetime import datetime

test_facts = [
        {
            'id': str(uuid.uuid4()),
            'variable': 'температура',
            'value': '39.5',
            'agent': 'expert1',
            'author': 'Система',
            'confidence': 0.95,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': str(uuid.uuid4()),
            'variable': 'давление',
            'value': '150/95',
            'agent': 'expert1',
            'author': 'Система',
            'confidence': 0.90,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    ]