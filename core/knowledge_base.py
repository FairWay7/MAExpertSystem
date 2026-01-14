from typing import List, Dict, Set


class KnowledgeBase:
    """База знаний для хранения и управления правилами и фактами"""

    def __init__(self, name: str = "База знаний"):
        self.name = name
        self.rules: Dict[str, Dict] = {}
        self.facts: Dict[str, Dict] = {}
        self.variables: Set[str] = set()
        self.agents: Dict[str, Dict] = {}
        self.domains: Dict[str, Dict] = {}

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

    def add_domain(self, domain: Dict) -> str:
        """Добавление предметной области"""
        domain_id = domain.get('id')
        if not domain_id:
            import uuid
            domain_id = str(uuid.uuid4())
            domain['id'] = domain_id

        self.domains[domain_id] = domain
        return domain_id

    def get_rules_by_agent(self, agent_id: str) -> List[Dict]:
        """Получение правил агента"""
        return [
            rule for rule in self.rules.values()
            if rule.get('agent_id') == agent_id
        ]

    def get_facts_by_agent(self, agent_id: str) -> List[Dict]:
        """Получение фактов агента"""
        return [
            fact for fact in self.facts.values()
            if fact.get('agent_id') == agent_id
        ]

    def get_rules_by_domain(self, domain_id: str) -> List[Dict]:
        """Получение правил домена"""
        return [
            rule for rule in self.rules.values()
            if rule.get('domain_id') == domain_id
        ]

    def get_facts_by_domain(self, domain_id: str) -> List[Dict]:
        """Получение фактов домена"""
        return [
            fact for fact in self.facts.values()
            if fact.get('domain_id') == domain_id
        ]

    def find_similar_rules(self, agent_id: str = None,
                           threshold: float = 0.7) -> List[Dict]:
        """Поиск схожих правил"""
        # Получаем правила для анализа
        if agent_id:
            rules = self.get_rules_by_agent(agent_id)
        else:
            rules = list(self.rules.values())

        similar_pairs = []

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                similarity = self._calculate_similarity(
                    rules[i]['condition'], rules[j]['condition']
                )

                if similarity >= threshold:
                    similar_pairs.append({
                        'rule1': rules[i],
                        'rule2': rules[j],
                        'similarity': similarity,
                        'type': self._determine_similarity_type(rules[i], rules[j])
                    })

        return similar_pairs

    def find_conflicting_rules(self, agent_id: str = None) -> List[Dict]:
        """Поиск конфликтных правил"""
        if agent_id:
            rules = self.get_rules_by_agent(agent_id)
        else:
            rules = list(self.rules.values())

        conflicting_pairs = []

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                # Проверяем схожесть условий
                condition_sim = self._calculate_similarity(
                    rule1['condition'], rule2['condition']
                )

                # Если условия схожи, но действия разные - конфликт
                if condition_sim > 0.8 and rule1['action'] != rule2['action']:
                    conflicting_pairs.append({
                        'rule1': rule1,
                        'rule2': rule2,
                        'condition_similarity': condition_sim,
                        'conflict_type': 'different_actions'
                    })

        return conflicting_pairs

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Вычисление схожести текстов"""
        if not text1 or not text2:
            return 0.0

        text1 = text1.lower()
        text2 = text2.lower()

        # Разбиваем на слова
        import re
        words1 = set(re.findall(r'\b\w+\b', text1))
        words2 = set(re.findall(r'\b\w+\b', text2))

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _determine_similarity_type(self, rule1: Dict, rule2: Dict) -> str:
        """Определение типа схожести"""
        cond_sim = self._calculate_similarity(rule1['condition'], rule2['condition'])
        act_sim = self._calculate_similarity(rule1['action'], rule2['action'])

        if cond_sim > 0.8 and act_sim > 0.8:
            return 'identical'
        elif cond_sim > 0.8:
            return 'same_condition'
        elif act_sim > 0.8:
            return 'same_action'
        else:
            return 'partial'

    def get_statistics(self) -> Dict:
        """Получение статистики"""
        return {
            'rules': len(self.rules),
            'facts': len(self.facts),
            'variables': len(self.variables),
            'agents': len(self.agents),
            'domains': len(self.domains)
        }