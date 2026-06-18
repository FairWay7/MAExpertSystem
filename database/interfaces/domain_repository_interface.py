from typing import Optional, Dict, List
from abc import ABC, abstractmethod

from database.interfaces.base.base_repository_interface import IBaseRepository


class IDomainRepository(ABC, IBaseRepository):
    @abstractmethod
    def create_domain(self, name: str, description: str = "") -> Optional[Dict]:
        pass

    @abstractmethod
    def get_domain(self, domain_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_domain_by_name(self, name: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_all_domains(self) -> List[Dict]:
        pass
