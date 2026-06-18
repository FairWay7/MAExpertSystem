from typing import Dict, List


class RuleService:
    def add_rule(self, rule: Dict) -> str:
        """Добавление правила в базу знаний"""
        rule_id = rule.get('id')
        if not rule_id:
            import uuid
            rule_id = str(uuid.uuid4())
            rule['id'] = rule_id

        # Проверяем на дубликаты
        for existing_rule in self.rules.values():
            if (existing_rule['condition'] == rule['condition'] and
                    existing_rule['action'] == rule['action']):
                return existing_rule['id']

        self.rules[rule_id] = rule

        # Обновляем статистику агента и домена
        if rule.get('agent_id'):
            agent_id = rule['agent_id']
            if agent_id in self.agents:
                if 'rules_count' not in self.agents[agent_id]:
                    self.agents[agent_id]['rules_count'] = 0
                self.agents[agent_id]['rules_count'] += 1

        if rule.get('domain_id'):
            domain_id = rule['domain_id']
            if domain_id in self.domains:
                if 'rules_count' not in self.domains[domain_id]:
                    self.domains[domain_id]['rules_count'] = 0
                self.domains[domain_id]['rules_count'] += 1

        return rule_id

    def get_rules_by_agent(self, agent_id: str) -> List[Dict]:
        """Получение правил агента"""
        return [
            rule for rule in self.rules.values()
            if rule.get('agent_id') == agent_id
        ]