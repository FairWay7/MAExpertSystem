from typing import Dict


class FactService:
    def add_fact(self, fact: Dict) -> str:
        """Добавление факта в базу знаний"""
        fact_id = fact.get('id')
        if not fact_id:
            import uuid
            fact_id = str(uuid.uuid4())
            fact['id'] = fact_id

        self.facts[fact_id] = fact
        self.variables.add(fact['variable_name'])

        # Обновляем статистику
        if fact.get('agent_id'):
            agent_id = fact['agent_id']
            if agent_id in self.agents:
                if 'facts_count' not in self.agents[agent_id]:
                    self.agents[agent_id]['facts_count'] = 0
                self.agents[agent_id]['facts_count'] += 1

        if fact.get('domain_id'):
            domain_id = fact['domain_id']
            if domain_id in self.domains:
                if 'facts_count' not in self.domains[domain_id]:
                    self.domains[domain_id]['facts_count'] = 0
                self.domains[domain_id]['facts_count'] += 1

        return fact_id
