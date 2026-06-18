from abc import ABC, abstractmethod
from typing import Optional, Dict, List

from database.interfaces.base.base_repository_interface import IBaseRepository


class IRuleRepository(ABC, IBaseRepository):
    @abstractmethod
    def save_rule(self, rule_data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_rule(self, rule_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_rules_by_agent(self, agent_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_rules_by_domain(self, domain_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_all_rules(self) -> List[Dict]:
        pass

    @abstractmethod
    def update_rule_priority(self, rule_id: str, priority: int) -> bool:
        pass

    @abstractmethod
    def delete_rule(self, rule_id: str) -> bool:
        pass

    @abstractmethod
    def find_similar_rules(self, agent_id: str = None, threshold: float = 0.7) -> List[Dict]:
        pass

    @abstractmethod
    def find_conflicting_rules(self, agent_id: str = None) -> List[Dict]:
        pass

    @abstractmethod
    def search_rules(self, query: str, agent_ids: List[str] = None) -> List[Dict]:
        pass