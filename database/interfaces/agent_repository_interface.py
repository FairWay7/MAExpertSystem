from typing import Optional, Dict, List
from abc import ABC, abstractmethod

from database.interfaces.base.base_repository_interface import IBaseRepository


class IAgentRepository(ABC, IBaseRepository):
    @abstractmethod
    def create_agent(self, name: str, domain_id: str = None, description: str = "") -> Optional[Dict]:
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_agents_by_domain(self, domain_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_all_agents(self) -> List[Dict]:
        pass