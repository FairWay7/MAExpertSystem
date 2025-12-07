from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class Fact:
    id: str
    variable_name: str
    value: Any
    agent_id: str
    source_file: str
    author: str
    created_date: datetime
    confidence: float = 1.0

    def to_dict(self):
        return {
            'id': self.id,
            'variable_name': self.variable_name,
            'value': self.value,
            'agent_id': self.agent_id,
            'source_file': self.source_file,
            'author': self.author,
            'created_date': self.created_date.isoformat(),
            'confidence': self.confidence
        }