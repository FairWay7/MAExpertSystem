from abc import abstractmethod, ABC
from typing import Dict


class StatisticsServiceInterface(ABC):
    @abstractmethod
    def get_statistics(self) -> Dict:
        pass
