from typing import List, Dict, Any, Set, Tuple
from models.rule import Rule, RuleType
from models.fact import Fact
from datetime import datetime
import uuid


class KnowledgeBase:
    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.rules: Dict[str, Rule] = {}
        self.facts: Dict[str, Fact] = {}
        self.variables: Set[str] = set()
        self.agents: Dict[str, Dict] = {}

    def add_rule(self, rule_data: Dict) -> Rule:
        """Добавление правила в базу знаний"""
        rule_id = str(uuid.uuid4())
        rule = Rule(
            id=rule_id,
            name=rule_data['name'],
            condition=rule_data['condition'],
            action=rule_data['action'],
            rule_type=RuleType(rule_data.get('rule_type', 'condition')),
            priority=rule_data.get('priority', 1),
            agent_id=rule_data['agent_id'],
            source_file=rule_data['source_file'],
            author=rule_data['author'],
            created_date=datetime.now(),
            confidence=rule_data.get('confidence', 1.0),
            tags=rule_data.get('tags', []),
            metadata=rule_data.get('metadata', {})
        )
        self.rules[rule_id] = rule
        return rule

    def add_fact(self, fact_data: Dict) -> Fact:
        """Добавление факта в рабочую память"""
        fact_id = str(uuid.uuid4())
        fact = Fact(
            id=fact_id,
            variable_name=fact_data['variable_name'],
            value=fact_data['value'],
            agent_id=fact_data['agent_id'],
            source_file=fact_data['source_file'],
            author=fact_data['author'],
            created_date=datetime.now(),
            confidence=fact_data.get('confidence', 1.0)
        )
        self.facts[fact_id] = fact
        self.variables.add(fact.variable_name)
        return fact

    def get_rules_by_agent(self, agent_id: str) -> List[Rule]:
        """Получение правил конкретного агента"""
        return [rule for rule in self.rules.values() if rule.agent_id == agent_id]

    def find_similar_rules(self, agent_id: str = None) -> List[Tuple[Rule, Rule]]:
        """Поиск схожих правил"""
        similar = []
        rules_list = list(self.rules.values())

        for i in range(len(rules_list)):
            for j in range(i + 1, len(rules_list)):
                rule1 = rules_list[i]
                rule2 = rules_list[j]

                if agent_id and (rule1.agent_id != agent_id and rule2.agent_id != agent_id):
                    continue

                similarity = self.calculate_rule_similarity(rule1, rule2)
                if similarity > 0.7:  # Порог схожести
                    similar.append((rule1, rule2, similarity))

        return similar

    def find_conflicting_rules(self, agent_id: str = None) -> List[Tuple[Rule, Rule]]:
        """Поиск конфликтных правил"""
        conflicting = []
        rules_list = list(self.rules.values())

        for i in range(len(rules_list)):
            for j in range(i + 1, len(rules_list)):
                rule1 = rules_list[i]
                rule2 = rules_list[j]

                if agent_id and (rule1.agent_id != agent_id and rule2.agent_id != agent_id):
                    continue

                if self.are_rules_conflicting(rule1, rule2):
                    conflicting.append((rule1, rule2))

        return conflicting

    def calculate_rule_similarity(self, rule1: Rule, rule2: Rule) -> float:
        """Вычисление степени схожести правил"""
        # Простая метрика схожести на основе текста
        from difflib import SequenceMatcher

        cond_sim = SequenceMatcher(None, rule1.condition, rule2.condition).ratio()
        action_sim = SequenceMatcher(None, rule1.action, rule2.action).ratio()

        return (cond_sim + action_sim) / 2

    def are_rules_conflicting(self, rule1: Rule, rule2: Rule) -> bool:
        """Проверка на конфликтность правил"""
        # Простая проверка: одинаковые условия, но разные действия
        cond_sim = self.calculate_rule_similarity(rule1, rule2)
        return cond_sim > 0.8 and rule1.action != rule2.action