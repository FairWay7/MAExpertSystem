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
