from dataclasses import dataclass


@dataclass
class Agent:
    id: int
    name: str
    domain_id: int
    description: str
    created_at: str