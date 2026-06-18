from abc import ABC, abstractmethod
from typing import Dict

from database.interfaces.base.base_repository_interface import IBaseRepository


class IStatisticsRepository(ABC, IBaseRepository):
    @abstractmethod
    def get_statistics(self) -> Dict:
        pass


