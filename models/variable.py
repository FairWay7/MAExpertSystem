from dataclasses import dataclass


@dataclass
class Variable:
    id: int
    name: str
    agent_id: int
    value_type: str
    description: str
    source_file: str
    author: str
    created_at: str