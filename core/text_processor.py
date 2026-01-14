import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class TextProcessor:
    """Обработчик текста для извлечения знаний"""

    def __init__(self, language: str = 'ru'):
        self.language = language
        self._init_patterns()

    def _init_patterns(self):
        """Инициализация паттернов для извлечения"""
        if self.language == 'ru':
            self.rule_patterns = [
                # Условные правила
                (r'если\s+(.+?)\s*[,;]\s*то\s+(.+)', 'conditional'),
                (r'когда\s+(.+?)\s*[,;]\s*тогда\s+(.+)', 'conditional'),
                (r'при\s+(.+?)\s*[,;]\s*происходит\s+(.+)', 'conditional'),
                # Причинно-следственные
                (r'(.+?)\s+приводит к\s+(.+)', 'causal'),
                (r'из-за\s+(.+?)\s+наступает\s+(.+)', 'causal'),
            ]

            self.fact_patterns = [
                # Определения
                (r'([А-ЯA-Z][А-Яа-яA-Za-z\s]{0,50}?)\s+[—\-]\s+это\s+(.+)', 0.9),
                (r'([А-ЯA-Z][А-Яа-яA-Za-z\s]{0,50}?)\s+является\s+(.+)', 0.8),
                # Равенства
                (r'([А-Яа-яA-Za-z_]+)\s*[=:]\s*(.+)', 0.7),
            ]
        else:
            self.rule_patterns = [
                (r'if\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional'),
                (r'when\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional'),
                (r'(.+?)\s+leads to\s+(.+)', 'causal'),
            ]

            self.fact_patterns = [
                (r'([A-Z][A-Za-z\s]{0,50}?)\s+is\s+(.+)', 0.9),
                (r'([A-Z][A-Za-z\s]{0,50}?)\s+means\s+(.+)', 0.8),
                (r'([A-Za-z_]+)\s*[=:]\s*(.+)', 0.7),
            ]

    def extract_from_text(self, text: str, source_info: Dict) -> Dict[str, List]:
        """
        Извлечение правил и фактов из текста

        Args:
            text: Исходный текст
            source_info: Информация об источнике

        Returns:
            Словарь с извлеченными правилами и фактами
        """
        # Очищаем текст
        text = self._clean_text(text)

        # Разбиваем на предложения
        sentences = self._split_sentences(text)

        rules = []
        facts = []

        for sentence in sentences:
            # Извлекаем правила
            rule = self._extract_rule(sentence, source_info)
            if rule:
                rules.append(rule)

            # Извлекаем факты
            fact = self._extract_fact(sentence, source_info)
            if fact:
                facts.append(fact)

        return {
            'rules': rules,
            'facts': facts,
            'statistics': {
                'sentences': len(sentences),
                'rules_found': len(rules),
                'facts_found': len(facts)
            }
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Разбиение текста на предложения"""
        if not text:
            return []

        # Простая разбивка по знакам препинания
        # Учитываем сокращения
        text = re.sub(r'([.!?])\s+', r'\1\n', text)

        sentences = []
        for sentence in text.split('\n'):
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)

        return sentences

    def _extract_rule(self, sentence: str, source_info: Dict) -> Optional[Dict]:
        """Извлечение правила из предложения"""
        for pattern, rule_type in self.rule_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                condition = self._clean_text(match.group(1))
                action = self._clean_text(match.group(2))

                # Пропускаем слишком короткие
                if len(condition) < 3 or len(action) < 3:
                    continue

                return {
                    'id': str(uuid.uuid4()),
                    'name': f"Правило из '{source_info.get('source_file', 'текст')}'",
                    'condition': condition,
                    'action': action,
                    'rule_type': rule_type,
                    'priority': 1,
                    'confidence': 0.8,
                    'source_file': source_info.get('source_file', ''),
                    'author': source_info.get('author', 'system'),
                    'tags': ['извлечено'],
                    'agent_id': source_info.get('agent_id'),
                    'domain_id': source_info.get('domain_id'),
                    'created_at': datetime.now().isoformat()
                }

        return None

    def _extract_fact(self, sentence: str, source_info: Dict) -> Optional[Dict]:
        """Извлечение факта из предложения"""
        for pattern, confidence in self.fact_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                variable = self._clean_text(match.group(1))
                value = self._clean_text(match.group(2))

                # Пропускаем слишком короткие
                if len(variable) < 2 or len(value) < 2:
                    continue

                return {
                    'id': str(uuid.uuid4()),
                    'variable_name': variable,
                    'value': value,
                    'confidence': confidence,
                    'source_file': source_info.get('source_file', ''),
                    'author': source_info.get('author', 'system'),
                    'is_derived': False,
                    'agent_id': source_info.get('agent_id'),
                    'domain_id': source_info.get('domain_id'),
                    'created_at': datetime.now().isoformat()
                }

        return None

    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ""

        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text)

        # Удаляем пробелы по краям
        text = text.strip()

        # Удаляем лишние знаки препинания в конце
        text = re.sub(r'[.,;]+$', '', text)

        return text

    def analyze_text_structure(self, text: str) -> Dict:
        """Анализ структуры текста"""
        sentences = self._split_sentences(text)

        # Подсчет потенциальных правил и фактов
        potential_rules = 0
        potential_facts = 0

        for sentence in sentences:
            # Проверяем на правила
            for pattern, _ in self.rule_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    potential_rules += 1
                    break

            # Проверяем на факты
            for pattern, _ in self.fact_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    potential_facts += 1
                    break

        return {
            'total_chars': len(text),
            'total_words': len(text.split()),
            'sentences': len(sentences),
            'potential_rules': potential_rules,
            'potential_facts': potential_facts
        }