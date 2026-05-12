from typing import Dict

from core.interfaces.statistics_service_interface import StatisticsServiceInterface


class StatisticsService(StatisticsServiceInterface):
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        return {
            'rules': len(self.rules),
            'facts': len(self.facts),
            'variables': len(self.variables),
            'agents': len(self.agents),
            'domains': len(self.domains)
        }