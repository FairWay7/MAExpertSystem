from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum


class RuleType(Enum):
    CONDITION = "condition"
    ACTION = "action"
    INFERENCE = "inference"


@dataclass
class Rule:
    id: str
    name: str
    condition: str  # Логическое выражение
    action: str  # Действие или вывод
    rule_type: RuleType
    priority: int
    agent_id: str
    source_file: str
    author: str
    created_date: datetime
    confidence: float = 1.0
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'condition': self.condition,
            'action': self.action,
            'rule_type': self.rule_type.value,
            'priority': self.priority,
            'agent_id': self.agent_id,
            'source_file': self.source_file,
            'author': self.author,
            'created_date': self.created_date.isoformat(),
            'confidence': self.confidence,
            'tags': self.tags,
            'metadata': self.metadata
        }