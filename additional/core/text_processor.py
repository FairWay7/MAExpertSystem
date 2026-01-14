import spacy
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict
import re


class TextProcessor:
    def __init__(self, language="ru"):
        self.language = language
        self.init_spacy()

        dependencies = ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'maxent_ne_chunker',
                        'words', 'stopwords']

        for dependence in dependencies:
            try:
                nltk.data.find(dependence)
            except LookupError:
                print(f'Отсутствует пакет {dependence}')
                nltk.download(dependence, quiet=True)
                print(f'Пакет {dependence} установлен')

    # Инициализация spaCy
    def init_spacy(self):
        try:
            if self.language == 'ru':
                self.nlp = spacy.load("ru_core_news_sm")
                # self.nlp = spacy.load("ru_core_news_lg")
            else:
                self.nlp = spacy.load("en_core_web_sm")
                # self.nlp = spacy.load("ru_core_news_lg")
        except OSError:
            # Простая обработка, если модель не найден
            self.nlp = None

    # Извлечение правил из текста
    def extract_rules_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        rules = []
        sentences = sent_tokenize(text, language="russian")

        for sentence in sentences:
            # Поиск условных конструкций
            if self.is_conditional_sentence(sentence):
                rule = self.parse_conditional_sentence(sentence, source_info)
                if rule:
                    rules.append(rule)

            # Поиск причинно-следственных связей
            elif self._is_causal_sentence(sentence):
                rule = self._parse_causal_sentence(sentence, source_info)
                if rule:
                    rules.append(rule)

        return rules

    def extract_facts_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение фактов из текста"""
        facts = []
        doc = self.nlp(text)

        # Извлечение именованных сущностей
        for ent in doc.ents:
            fact = {
                'variable_name': f"entity_{ent.label_}",
                'value': ent.text,
                'agent_id': source_info['agent_id'],
                'source_file': source_info['source_file'],
                'author': source_info['author'],
                'confidence': 0.9
            }
            facts.append(fact)

        # Извлечение фактов через синтаксический анализ
        for sentence in doc.sents:
            facts.extend(self._extract_facts_from_sentence(sentence, source_info))

        return facts

    def is_conditional_sentence(self, sentence: str) -> bool:
        """Проверка, является ли предложение условным"""
        condition_keywords = ['если', 'при условии', 'в случае', 'когда']
        return any(keyword in sentence.lower() for keyword in condition_keywords)

    def parse_conditional_sentence(self, sentence: str, source_info: Dict) -> Dict:
        """Разбор условного предложения в правило"""
        # Простой парсер для условных конструкций
        match = re.match(r'(.+?) (то|тогда) (.+)', sentence, re.IGNORECASE)
        if match:
            condition = match.group(1)
            action = match.group(3)

            return {
                'name': f"Правило из {source_info['source_file']}",
                'condition': condition.strip(),
                'action': action.strip(),
                'rule_type': 'condition',
                'priority': 1,
                'agent_id': source_info['agent_id'],
                'source_file': source_info['source_file'],
                'author': source_info['author']
            }
        return None