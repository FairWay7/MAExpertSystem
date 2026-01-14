from dataclasses import dataclass


@dataclass
class Rule:
    id: str
    name: str
    condition: str  # Логическое выражение
    action: str  # Действие или вывод
    priority: int
    agent_id: str
    source_file: str
    author: str
    is_active: bool
    created_at: str

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'agent_id': self.agent_id,
            'source_file': self.source_file,
            'author': self.author,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
