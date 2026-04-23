from typing import Optional, Dict, List
from abc import ABC, abstractmethod

from database.interfaces.base.base_repository_interface import IBaseRepository


class IFactRepository(ABC, IBaseRepository):
    @abstractmethod
    def save_fact(self, fact_data: Dict) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_fact(self, fact_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_facts_by_agent(self, agent_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_facts_by_variable(self, variable_name: str, agent_id: str = None) -> List[Dict]:
        pass

    @abstractmethod
    def get_all_facts(self) -> List[Dict]:
        pass