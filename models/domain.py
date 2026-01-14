from dataclasses import dataclass


@dataclass
class Domain:
    id: int
    name: str
    description: str
    created_at: str