from typing import Dict


class AgentService:
    def add_agent(self, agent: Dict) -> str:
        """Добавление агента"""
        agent_id = agent.get('id')
        if not agent_id:
            import uuid
            agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            agent['id'] = agent_id

        self.agents[agent_id] = agent

        # Обновляем статистику домена
        if agent.get('domain_id'):
            domain_id = agent['domain_id']
            if domain_id in self.domains:
                if 'agents_count' not in self.domains[domain_id]:
                    self.domains[domain_id]['agents_count'] = 0
                self.domains[domain_id]['agents_count'] += 1

        return agent_id
