class Domain:
    """Предметная область"""

    def __init__(self, id, name, description="", created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.rules_count = 0
        self.facts_count = 0
        self.agents_count = 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'rules_count': self.rules_count,
            'facts_count': self.facts_count,
            'agents_count': self.agents_count
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description', ''),
            created_at=data.get('created_at')
        )


class Agent:
    """Агент (эксперт)"""

    def __init__(self, id, name, domain_id=None, description="", created_at=None):
        self.id = id
        self.name = name
        self.domain_id = domain_id
        self.description = description
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain_id': self.domain_id,
            'description': self.description,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            domain_id=data.get('domain_id'),
            description=data.get('description', ''),
            created_at=data.get('created_at')
        )


class Rule:
    """Продукционное правило"""

    def __init__(self, id, name, condition, action, rule_type="conditional",
                 priority=1, confidence=1.0, agent_id=None, domain_id=None,
                 source_file="", author="", tags=None, created_at=None):
        self.id = id
        self.name = name
        self.condition = condition
        self.action = action
        self.rule_type = rule_type
        self.priority = priority
        self.confidence = confidence
        self.agent_id = agent_id
        self.domain_id = domain_id
        self.source_file = source_file
        self.author = author
        self.tags = tags or []
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'condition': self.condition,
            'action': self.action,
            'rule_type': self.rule_type,
            'priority': self.priority,
            'confidence': self.confidence,
            'agent_id': self.agent_id,
            'domain_id': self.domain_id,
            'source_file': self.source_file,
            'author': self.author,
            'tags': self.tags,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            condition=data.get('condition'),
            action=data.get('action'),
            rule_type=data.get('rule_type', 'conditional'),
            priority=data.get('priority', 1),
            confidence=data.get('confidence', 1.0),
            agent_id=data.get('agent_id'),
            domain_id=data.get('domain_id'),
            source_file=data.get('source_file', ''),
            author=data.get('author', ''),
            tags=data.get('tags', []),
            created_at=data.get('created_at')
        )


class Fact:
    """Факт (утверждение)"""

    def __init__(self, id, variable_name, value, agent_id=None, domain_id=None,
                 confidence=1.0, source_file="", author="", is_derived=False,
                 created_at=None):
        self.id = id
        self.variable_name = variable_name
        self.value = value
        self.agent_id = agent_id
        self.domain_id = domain_id
        self.confidence = confidence
        self.source_file = source_file
        self.author = author
        self.is_derived = is_derived
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'variable_name': self.variable_name,
            'value': self.value,
            'agent_id': self.agent_id,
            'domain_id': self.domain_id,
            'confidence': self.confidence,
            'source_file': self.source_file,
            'author': self.author,
            'is_derived': self.is_derived,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            variable_name=data.get('variable_name'),
            value=data.get('value'),
            agent_id=data.get('agent_id'),
            domain_id=data.get('domain_id'),
            confidence=data.get('confidence', 1.0),
            source_file=data.get('source_file', ''),
            author=data.get('author', ''),
            is_derived=data.get('is_derived', False),
            created_at=data.get('created_at')
        )