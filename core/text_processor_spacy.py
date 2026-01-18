import re
import uuid
import spacy
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from spacy.matcher import Matcher
from spacy.language import Language


class TextProcessor:
    """Обработчик текста для извлечения знаний с использованием spaCy"""

    def __init__(self, language: str = 'ru'):
        self.language = language
        self._init_spacy_model()
        self._init_patterns()
        self._init_matchers()

    def _init_spacy_model(self):
        """Инициализация модели spaCy"""
        try:
            if self.language == 'ru':
                # Для русского языка
                self.nlp = spacy.load("ru_core_news_sm")
            else:
                # Для английского языка
                self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print(f"Модель spaCy для языка '{self.language}' не найдена.")
            print("Установите модель: python -m spacy download ru_core_news_sm")
            # Используем пустую модель в случае ошибки
            self.nlp = spacy.blank(self.language)

    def _init_patterns(self):
        """Инициализация паттернов для извлечения"""
        if self.language == 'ru':
            self.rule_patterns = [
                # Условные правила (улучшенные паттерны)
                (r'если\s+(.+?)\s*[,;]\s*то\s+(.+)', 'conditional'),
                (r'когда\s+(.+?)\s*[,;]\s*тогда\s+(.+)', 'conditional'),
                (r'при\s+(.+?)\s*[,;]\s*происходит\s+(.+)', 'conditional'),
                (r'в\s+случае\s+(.+?)\s*[,;]\s*наступает\s+(.+)', 'conditional'),
                
                # Причинно-следственные
                (r'(.+?)\s+приводит к\s+(.+)', 'causal'),
                (r'из-за\s+(.+?)\s+наступает\s+(.+)', 'causal'),
                (r'(.+?)\s+вызывает\s+(.+)', 'causal'),
                (r'следствием\s+(.+?)\s+является\s+(.+)', 'causal'),
                
                # Определения и свойства
                (r'(.+?)\s+определяется как\s+(.+)', 'definition'),
                (r'(.+?)\s+свойство\s+(.+)', 'property'),
            ]

            self.fact_patterns = [
                # Определения с использованием именованных сущностей
                (r'([А-ЯA-Z][А-Яа-яA-Za-z\s\-]{0,50}?)\s+[—\-]\s+это\s+(.+)', 0.9),
                (r'([А-ЯA-Z][А-Яа-яA-Za-z\s\-]{0,50}?)\s+является\s+(.+)', 0.8),
                (r'([А-ЯA-Z][А-Яа-яA-Za-z\s\-]{0,50}?)\s+представляет собой\s+(.+)', 0.85),
                
                # Равенства и присваивания
                (r'([А-Яа-яA-Za-z_]+)\s*[=:]\s*(.+)', 0.7),
                (r'значение\s+([А-Яа-яA-Za-z_]+)\s*[=:]\s*(.+)', 0.8),
                
                # Количественные утверждения
                (r'([А-Яа-яA-Za-z_]+)\s+равно\s+(.+)', 0.75),
                (r'([А-Яа-яA-Za-z_]+)\s+составляет\s+(.+)', 0.75),
            ]
        else:
            self.rule_patterns = [
                (r'if\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional'),
                (r'when\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional'),
                (r'(.+?)\s+leads to\s+(.+)', 'causal'),
                (r'(.+?)\s+causes\s+(.+)', 'causal'),
            ]

            self.fact_patterns = [
                (r'([A-Z][A-Za-z\s\-]{0,50}?)\s+is\s+(.+)', 0.9),
                (r'([A-Z][A-Za-z\s\-]{0,50}?)\s+means\s+(.+)', 0.8),
                (r'([A-Za-z_]+)\s*[=:]\s*(.+)', 0.7),
            ]

    def _init_matchers(self):
        """Инициализация матчеров spaCy для извлечения структур"""
        self.matcher = Matcher(self.nlp.vocab)
        
        if self.language == 'ru':
            # Паттерны для извлечения условий
            condition_patterns = [
                [{"LOWER": "если"}, {"OP": "*"}, {"IS_PUNCT": True, "OP": "?"}, {"OP": "*"}],
                [{"LOWER": "когда"}, {"OP": "*"}, {"IS_PUNCT": True, "OP": "?"}, {"OP": "*"}],
                [{"LOWER": "при"}, {"OP": "*"}, {"IS_PUNCT": True, "OP": "?"}, {"OP": "*"}],
            ]
            
            # Паттерны для извлечения следствий
            action_patterns = [
                [{"LOWER": "то"}, {"OP": "*"}],
                [{"LOWER": "тогда"}, {"OP": "*"}],
                [{"LOWER": "происходит"}, {"OP": "*"}],
                [{"LOWER": "наступает"}, {"OP": "*"}],
            ]
            
            # Паттерны для определений
            definition_patterns = [
                [{"POS": "PROPN", "OP": "+"}, {"LOWER": "это"}, {"OP": "*"}],
                [{"POS": "PROPN", "OP": "+"}, {"LOWER": "является"}, {"OP": "*"}],
            ]
            
        else:
            # Английские паттерны
            condition_patterns = [
                [{"LOWER": "if"}, {"OP": "*"}, {"IS_PUNCT": True, "OP": "?"}, {"OP": "*"}],
                [{"LOWER": "when"}, {"OP": "*"}, {"IS_PUNCT": True, "OP": "?"}, {"OP": "*"}],
            ]
            
            action_patterns = [
                [{"LOWER": "then"}, {"OP": "*"}],
                [{"LOWER": "therefore"}, {"OP": "*"}],
            ]
            
            definition_patterns = [
                [{"POS": "PROPN", "OP": "+"}, {"LOWER": "is"}, {"OP": "*"}],
                [{"POS": "PROPN", "OP": "+"}, {"LOWER": "means"}, {"OP": "*"}],
            ]
        
        # Добавляем паттерны в матчер
        self.matcher.add("CONDITION", condition_patterns)
        self.matcher.add("ACTION", action_patterns)
        self.matcher.add("DEFINITION", definition_patterns)

    def extract_from_text(self, text: str, source_info: Dict) -> Dict[str, List]:
        """
        Извлечение правил и фактов из текста с использованием spaCy
        """
        # Очищаем текст
        text = self._clean_text(text)
        
        # Обрабатываем текст с помощью spaCy
        doc = self.nlp(text)
        
        # Разбиваем на предложения через spaCy
        sentences = list(doc.sents)
        
        rules = []
        facts = []
        
        for sentence in sentences:
            sent_text = sentence.text.strip()
            
            # Извлекаем правила с использованием комбинированного подхода
            rule = self._extract_rule_spacy(sentence, source_info)
            if not rule:
                # Если spaCy не нашел, используем регулярные выражения
                rule = self._extract_rule_regex(sent_text, source_info)
            
            if rule:
                rules.append(rule)
            
            # Извлекаем факты с использованием комбинированного подхода
            fact = self._extract_fact_spacy(sentence, source_info)
            if not fact:
                # Если spaCy не нашел, используем регулярные выражения
                fact = self._extract_fact_regex(sent_text, source_info)
            
            if fact:
                facts.append(fact)
        
        return {
            'rules': rules,
            'facts': facts,
            'statistics': {
                'sentences': len(sentences),
                'rules_found': len(rules),
                'facts_found': len(facts),
                'entities': len(doc.ents)
            }
        }

    def _extract_rule_spacy(self, sentence, source_info: Dict) -> Optional[Dict]:
        """Извлечение правила с использованием spaCy"""
        matches = self.matcher(sentence)
        
        if not matches:
            return None
        
        # Ищем условия и действия в предложении
        condition_text = ""
        action_text = ""
        
        # Анализируем структуру предложения
        for token in sentence:
            # Проверяем наличие подчинительных союзов для условий
            if token.dep_ in ("mark", "advmod") and token.lower_ in ("если", "когда", "при", "if", "when"):
                # Извлекаем зависимое предложение
                subtree = list(token.subtree)
                if subtree:
                    condition_start = min(t.i for t in subtree)
                    condition_end = max(t.i for t in subtree) + 1
                    condition_text = sentence[condition_start:condition_end].text
                    
                    # Ищем главное предложение (действие)
                    for child in token.head.children:
                        if child.dep_ in ("conj", "advcl", "ccomp"):
                            action_start = min(t.i for t in child.subtree)
                            action_end = max(t.i for t in child.subtree) + 1
                            action_text = sentence[action_start:action_end].text
        
        # Если не нашли через зависимости, используем матчер
        if not condition_text or not action_text:
            for match_id, start, end in matches:
                span = sentence[start:end]
                if self.nlp.vocab.strings[match_id] == "CONDITION":
                    condition_text = span.text
                    # Ищем следующее совпадение для действия
                    for match_id2, start2, end2 in matches:
                        if start2 > end and self.nlp.vocab.strings[match_id2] == "ACTION":
                            action_text = sentence[start2:end2].text
                            break
        
        condition_text = self._clean_text(condition_text)
        action_text = self._clean_text(action_text)
        
        if len(condition_text) < 3 or len(action_text) < 3:
            return None
        
        # Определяем тип правила на основе содержания
        rule_type = self._determine_rule_type(condition_text, action_text, sentence)
        
        return {
            'id': str(uuid.uuid4()),
            'name': f"Правило из '{source_info.get('source_file', 'текст')}'",
            'condition': condition_text,
            'action': action_text,
            'rule_type': rule_type,
            'priority': 1,
            'confidence': self._calculate_confidence(sentence.text),
            'source_file': source_info.get('source_file', ''),
            'author': source_info.get('author', 'system'),
            'tags': ['извлечено', 'spacy'],
            'agent_id': source_info.get('agent_id'),
            'domain_id': source_info.get('domain_id'),
            'created_at': datetime.now().isoformat(),
            'linguistic_features': self._extract_linguistic_features(sentence)
        }

    def _extract_rule_regex(self, sentence: str, source_info: Dict) -> Optional[Dict]:
        """Извлечение правила с использованием регулярных выражений"""
        for pattern, rule_type in self.rule_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                condition = self._clean_text(match.group(1))
                action = self._clean_text(match.group(2))
                
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
                    'tags': ['извлечено', 'regex'],
                    'agent_id': source_info.get('agent_id'),
                    'domain_id': source_info.get('domain_id'),
                    'created_at': datetime.now().isoformat()
                }
        
        return None

    def _extract_fact_spacy(self, sentence, source_info: Dict) -> Optional[Dict]:
        """Извлечение факта с использованием spaCy"""
        # Извлекаем именованные сущности
        entities = list(sentence.ents)
        
        # Ищем паттерны определений
        matches = self.matcher(sentence)
        
        for match_id, start, end in matches:
            if self.nlp.vocab.strings[match_id] == "DEFINITION":
                span = sentence[start:end]
                
                # Пытаемся извлечь переменную и значение
                # Ищем именованные сущности в span
                variable = ""
                value = ""
                
                # Первая именованная сущность или существительное
                for token in span:
                    if token.ent_type_ or token.pos_ in ("PROPN", "NOUN"):
                        variable = token.text
                        break
                
                # Значение - остальная часть span
                value_start = span.start + 1
                if value_start < span.end:
                    value = sentence[value_start:span.end].text
                
                variable = self._clean_text(variable)
                value = self._clean_text(value)
                
                if len(variable) < 2 or len(value) < 2:
                    continue
                
                # Рассчитываем уверенность на основе лингвистических признаков
                confidence = self._calculate_fact_confidence(sentence, variable, value)
                
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
                    'created_at': datetime.now().isoformat(),
                    'entity_type': self._get_entity_type(variable, sentence)
                }
        
        return None

    def _extract_fact_regex(self, sentence: str, source_info: Dict) -> Optional[Dict]:
        """Извлечение факта с использованием регулярных выражений"""
        for pattern, confidence in self.fact_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                variable = self._clean_text(match.group(1))
                value = self._clean_text(match.group(2))
                
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

    def _determine_rule_type(self, condition: str, action: str, sentence) -> str:
        """Определение типа правила на основе лингвистического анализа"""
        # Анализируем слова в условии и действии
        condition_doc = self.nlp(condition)
        action_doc = self.nlp(action)
        
        # Проверяем наличие причинных маркеров
        causal_markers = ["приводит", "вызывает", "влечет", "leads", "causes"]
        
        for marker in causal_markers:
            if marker in condition.lower() or marker in action.lower():
                return "causal"
        
        # Проверяем временные отношения
        temporal_markers = ["когда", "после", "до", "when", "after", "before"]
        for marker in temporal_markers:
            if marker in condition.lower():
                return "temporal"
        
        # Проверяем наличие модальных глаголов
        modal_verbs = ["должен", "может", "следует", "must", "should", "can"]
        for token in action_doc:
            if token.lemma_ in modal_verbs:
                return "obligation"
        
        return "conditional"

    def _calculate_confidence(self, text: str) -> float:
        """Расчет уверенности в извлеченном правиле"""
        doc = self.nlp(text)
        
        confidence = 0.5  # Базовая уверенность
        
        # Увеличиваем уверенность за наличие определенных структур
        if any(token.dep_ == "mark" for token in doc):  # Есть подчинительные союзы
            confidence += 0.2
        
        if any(token.pos_ == "VERB" for token in doc):  # Есть глаголы
            confidence += 0.1
        
        if len(doc.ents) > 0:  # Есть именованные сущности
            confidence += 0.1
        
        # Уменьшаем уверенность за сложные конструкции
        if len(list(doc.sents)) > 1:  # Сложное предложение
            confidence -= 0.1
        
        return min(max(confidence, 0.1), 1.0)

    def _calculate_fact_confidence(self, sentence, variable: str, value: str) -> float:
        """Расчет уверенности в извлеченном факте"""
        confidence = 0.5
        
        # Проверяем, является ли переменная именованной сущностью
        for ent in sentence.ents:
            if variable in ent.text:
                confidence += 0.2
                break
        
        # Проверяем наличие числового значения
        if any(char.isdigit() for char in value):
            confidence += 0.1
        
        # Проверяем наличие определенных частей речи
        variable_doc = self.nlp(variable)
        if any(token.pos_ in ("NOUN", "PROPN") for token in variable_doc):
            confidence += 0.1
        
        return min(max(confidence, 0.1), 1.0)

    def _extract_linguistic_features(self, sentence):
        """Извлечение лингвистических признаков из предложения"""
        features = {
            'tokens': len(sentence),
            'verbs': sum(1 for token in sentence if token.pos_ == "VERB"),
            'nouns': sum(1 for token in sentence if token.pos_ in ("NOUN", "PROPN")),
            'entities': [ent.text for ent in sentence.ents],
            'entity_types': [ent.label_ for ent in sentence.ents],
            'dependency_tree': [(token.text, token.dep_, token.head.text) 
                              for token in sentence[:10]]  # Ограничиваем для удобства
        }
        return features

    def _get_entity_type(self, text: str, sentence) -> str:
        """Определение типа именованной сущности"""
        for ent in sentence.ents:
            if text in ent.text:
                return ent.label_
        
        # Определяем по морфологическим признакам
        doc = self.nlp(text)
        if doc:
            token = doc[0]
            if token.pos_ == "PROPN":
                return "PROPER_NOUN"
            elif token.pos_ == "NOUN":
                return "COMMON_NOUN"
        
        return "UNKNOWN"

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
        
        # Удаляем кавычки и скобки по краям
        text = re.sub(r'^[\"\'\(\[\{]+|[\"\'\)\]\}]+$', '', text)
        
        return text

    def analyze_text_structure(self, text: str) -> Dict:
        """Анализ структуры текста с использованием spaCy"""
        doc = self.nlp(text)
        sentences = list(doc.sents)
        
        # Подсчет потенциальных правил и фактов
        potential_rules = 0
        potential_facts = 0
        
        # Анализ с использованием spaCy
        for sentence in sentences:
            sent_text = sentence.text
            
            # Проверяем на правила через spaCy матчер
            matches = self.matcher(sentence)
            rule_matches = [m for m in matches if self.nlp.vocab.strings[m[0]] in ("CONDITION", "ACTION")]
            if len(rule_matches) >= 2:  # Нужно хотя бы условие и действие
                potential_rules += 1
            
            # Проверяем на факты через spaCy
            definition_matches = [m for m in matches if self.nlp.vocab.strings[m[0]] == "DEFINITION"]
            if definition_matches:
                potential_facts += 1
            
            # Дополнительная проверка через регулярные выражения
            for pattern, _ in self.rule_patterns:
                if re.search(pattern, sent_text, re.IGNORECASE):
                    potential_rules += 1
                    break
            
            for pattern, _ in self.fact_patterns:
                if re.search(pattern, sent_text, re.IGNORECASE):
                    potential_facts += 1
                    break
        
        # Статистика именованных сущностей
        entity_stats = {}
        for ent in doc.ents:
            entity_stats[ent.label_] = entity_stats.get(ent.label_, 0) + 1
        
        # Статистика частей речи
        pos_stats = {}
        for token in doc:
            if not token.is_punct and not token.is_space:
                pos_stats[token.pos_] = pos_stats.get(token.pos_, 0) + 1
        
        return {
            'total_chars': len(text),
            'total_words': len([token for token in doc if not token.is_punct and not token.is_space]),
            'sentences': len(sentences),
            'potential_rules': potential_rules,
            'potential_facts': potential_facts,
            'entities': len(doc.ents),
            'entity_stats': entity_stats,
            'pos_stats': pos_stats,
            'readability_score': self._calculate_readability(doc)
        }

    def _calculate_readability(self, doc) -> float:
        """Расчет показателя читабельности текста"""
        if len(list(doc.sents)) == 0:
            return 0.0
        
        # Простая метрика: средняя длина предложения в словах
        sentences = list(doc.sents)
        avg_sentence_length = sum(len([t for t in sent if not t.is_punct]) for sent in sentences) / len(sentences)
        
        # Нормализуем к шкале 0-1 (чем короче предложения, тем читабельнее)
        readability = max(0, 1 - (avg_sentence_length / 50))
        
        return round(readability, 2)

    def extract_key_concepts(self, text: str) -> List[Dict]:
        """Извлечение ключевых концепций из текста"""
        doc = self.nlp(text)
        
        concepts = []
        
        # Извлекаем именованные сущности
        for ent in doc.ents:
            concepts.append({
                'text': ent.text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'source': 'named_entity'
            })
        
        # Извлекаем существительные и прилагательные
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Игнорируем одиночные слова
                concepts.append({
                    'text': chunk.text,
                    'type': 'NOUN_PHRASE',
                    'start': chunk.start_char,
                    'end': chunk.end_char,
                    'source': 'noun_chunk'
                })
        
        # Убираем дубликаты
        unique_concepts = []
        seen = set()
        for concept in concepts:
            key = (concept['text'], concept['type'])
            if key not in seen:
                seen.add(key)
                unique_concepts.append(concept)
        
        return unique_concepts

    def extract_relationships(self, text: str) -> List[Dict]:
        """Извлечение отношений между сущностями"""
        doc = self.nlp(text)
        relationships = []
        
        # Ищем глаголы и их субъекты/объекты
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                # Находим субъект и объект
                subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubj:pass")]
                objects = [child for child in token.children if child.dep_ in ("obj", "iobj", "obl")]
                
                for subj in subjects:
                    for obj in objects:
                        relationships.append({
                            'subject': subj.text,
                            'relation': token.lemma_,
                            'object': obj.text,
                            'sentence': token.sent.text[:100] + "..."
                        })
        
        return relationships