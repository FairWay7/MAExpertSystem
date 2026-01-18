import spacy
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict
import re
import os
import sys
from io import StringIO

class TextProcessor:
    def __init__(self, language='ru'):
        self.language = language  # 'ru' или 'en'
        self.nlp = None
        
        # Тихая инициализация NLTK
        self._quiet_nltk_init()
        
        # Инициализация spaCy
        self._init_spacy()
    
    def _quiet_nltk_init(self):
        """Тихая инициализация NLTK ресурсов"""
        try:
            # Проверяем наличие punkt
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            # Подавляем вывод при загрузке
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                nltk.download('punkt', quiet=True)
            finally:
                sys.stdout = old_stdout
    
    def _init_spacy(self):
        """Инициализация spaCy"""
        try:
            if self.language == 'ru':
                self.nlp = spacy.load("ru_core_news_sm")
            else:
                self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Используем простую обработку если модель не найдена
            self.nlp = None
    
    def extract_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение правил из текста"""
        rules = []
        
        # Используем безопасную токенизацию предложений
        sentences = self.safe_sentence_tokenize(text)
        
        for sentence in sentences:
            # Поиск условных конструкций
            if self.is_conditional_sentence(sentence):
                rule = self.parse_conditional_sentence(sentence, source_info)
                if rule:
                    rules.append(rule)
            
            # Поиск причинно-следственных связей
            elif self.is_causal_sentence(sentence):
                rule = self.parse_causal_sentence(sentence, source_info)
                if rule:
                    rules.append(rule)
            
            # Поиск определений
            elif self.is_definition_sentence(sentence):
                fact = self._parse_definition_sentence(sentence, source_info)
                if fact:
                    # Создаем правило из определения
                    rule = {
                        'name': f"Определение из {source_info['source_file']}",
                        'condition': f"запрос_определения('{fact['variable_name']}')",
                        'action': f"{fact['variable_name']} = '{fact['value']}'",
                        'rule_type': 'definition',
                        'priority': 1,
                        'agent_id': source_info['agent_id'],
                        'source_file': source_info['source_file'],
                        'author': source_info['author']
                    }
                    rules.append(rule)
        
        return rules
    
    def safe_sentence_tokenize(self, text: str, max_length=100000) -> List[str]:
        """
        Безопасная токенизация предложений с защитой от переполнения стека
        
        Args:
            text: Входной текст
            max_length: Максимальная длина текста для обработки за раз
            
        Returns:
            List[str]: Список предложений
        """
        if not text:
            return []
        
        # Если текст слишком длинный, разбиваем его на части
        if len(text) > max_length:
            sentences = []
            for i in range(0, len(text), max_length):
                chunk = text[i:i + max_length]
                chunk_sentences = self.tokenize_single_chunk(chunk)
                sentences.extend(chunk_sentences)
            return sentences
        
        return self.tokenize_single_chunk(text)
    
    def tokenize_single_chunk(self, text_chunk: str) -> List[str]:
        """Токенизация одного фрагмента текста"""
        try:
            # Преобразуем код языка в название для NLTK
            language_name = 'russian' if self.language == 'ru' else 'english'
            
            # Пробуем токенизацию с указанием языка
            sentences = sent_tokenize(text_chunk, language=language_name)
            return [s.strip() for s in sentences if s.strip()]
            
        except Exception as e:
            # Если возникает ошибка, используем простую разбивку
            print(f"Ошибка при токенизации NLTK: {e}. Использую простую разбивку.")
            
            # Простая разбивка по точкам, вопросительным и восклицательным знакам
            import re
            sentences = re.split(r'[.!?]+', text_chunk)
            return [s.strip() for s in sentences if s.strip()]
    
    def extract_facts_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение фактов из текста"""
        facts = []
        
        if self.nlp is None:
            return self.simple_fact_extraction(text, source_info)
        
        try:
            # Ограничиваем длину текста для spaCy
            if len(text) > 1000000:  # 1MB limit
                text = text[:1000000]
            
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
            
            # Простое извлечение фактов по шаблонам
            facts.extend(self.extract_facts_by_patterns(text, source_info))
                
        except Exception as e:
            print(f"Ошибка при обработке текста spaCy: {e}")
            facts = self.simple_fact_extraction(text, source_info)
        
        return facts
    
    def extract_facts_by_patterns(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение фактов по шаблонам"""
        facts = []
        
        # Шаблоны для русского языка
        if self.language == 'ru':
            patterns = [
                # X - это Y
                (r'([А-Яа-яЁё][А-Яа-яЁё\s]{1,50}?)\s+[—\-]\s+это\s+([А-Яа-яЁё].+?)(?=[.!?])', 1.0),
                # X это Y
                (r'([А-Яа-яЁё][А-Яа-яЁё\s]{1,50}?)\s+это\s+([А-Яа-яЁё].+?)(?=[.!?])', 0.9),
                # X является Y
                (r'([А-Яа-яЁё][А-Яа-яЁё\s]{1,50}?)\s+является\s+([А-Яа-яЁё].+?)(?=[.!?])', 0.9),
                # X = число
                (r'([А-Яа-яЁёA-Za-z_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)', 0.8),
            ]
        else:
            # Шаблоны для английского языка
            patterns = [
                # X is Y
                (r'([A-Z][A-Za-z\s]{1,50}?)\s+is\s+([A-Z].+?)(?=[.!?])', 1.0),
                # X means Y
                (r'([A-Z][A-Za-z\s]{1,50}?)\s+means\s+([A-Z].+?)(?=[.!?])', 0.9),
                # X refers to Y
                (r'([A-Z][A-Za-z\s]{1,50}?)\s+refers to\s+([A-Z].+?)(?=[.!?])', 0.9),
                # X = number
                (r'([A-Za-z_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)', 0.8),
            ]
        
        for pattern, confidence in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Пропускаем слишком короткие или слишком длинные значения
                variable = match.group(1).strip()
                value = match.group(2).strip()
                
                if len(variable) > 100 or len(value) > 500:
                    continue
                
                fact = {
                    'variable_name': variable,
                    'value': value,
                    'agent_id': source_info['agent_id'],
                    'source_file': source_info['source_file'],
                    'author': source_info['author'],
                    'confidence': confidence
                }
                facts.append(fact)
        
        return facts
    
    def simple_fact_extraction(self, text: str, source_info: Dict) -> List[Dict]:
        """Простое извлечение фактов без spaCy"""
        return self.extract_facts_by_patterns(text, source_info)
    
    def is_conditional_sentence(self, sentence: str) -> bool:
        """Проверка, является ли предложение условным"""
        if self.language == 'ru':
            condition_keywords = ['если', 'при условии', 'в случае', 'когда', 'при']
        else:
            condition_keywords = ['if', 'when', 'provided that', 'in case', 'assuming']
        
        return any(keyword in sentence.lower() for keyword in condition_keywords)
    
    def is_causal_sentence(self, sentence: str) -> bool:
        """Проверка, является ли предложение причинно-следственным"""
        if self.language == 'ru':
            causal_keywords = ['потому что', 'так как', 'из-за', 'вследствие', 'поэтому']
        else:
            causal_keywords = ['because', 'since', 'due to', 'as a result', 'therefore']
        
        return any(keyword in sentence.lower() for keyword in causal_keywords)
    
    def is_definition_sentence(self, sentence: str) -> bool:
        """Проверка, является ли предложение определением"""
        if self.language == 'ru':
            definition_patterns = [r'\bэто\b', r'\bявляется\b', r'\bозначает\b', r'\bназывается\b']
        else:
            definition_patterns = [r'\bis\b', r'\bmeans\b', r'\brefers to\b', r'\bis called\b']
        
        return any(re.search(pattern, sentence, re.IGNORECASE) for pattern in definition_patterns)
    
    def parse_conditional_sentence(self, sentence: str, source_info: Dict) -> Dict:
        """Разбор условного предложения в правило"""
        if self.language == 'ru':
            patterns = [
                r'если\s+(.+?)\s*,\s*(?:то|тогда)\s+(.+)',
                r'при\s+(.+?)\s*,\s*(?:происходит|наступает|возникает)\s+(.+)',
                r'в случае\s+(.+?)\s*,\s*(?:имеем|получаем)\s+(.+)',
                r'когда\s+(.+?)\s*,\s*(?:тогда|то)\s+(.+)'
            ]
        else:
            patterns = [
                r'if\s+(.+?)\s*,\s*(?:then)?\s*(.+)',
                r'when\s+(.+?)\s*,\s*(.+)',
                r'in case of\s+(.+?)\s*,\s*(.+)',
                r'provided that\s+(.+?)\s*,\s*(.+)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                condition = match.group(1).strip().rstrip(',.')
                action = match.group(2).strip().rstrip('.')
                
                # Очищаем от лишних пробелов
                condition = re.sub(r'\s+', ' ', condition)
                action = re.sub(r'\s+', ' ', action)
                
                return {
                    'name': f"Условное правило из {source_info['source_file']}",
                    'condition': condition,
                    'action': action,
                    'rule_type': 'condition',
                    'priority': 1,
                    'agent_id': source_info['agent_id'],
                    'source_file': source_info['source_file'],
                    'author': source_info['author']
                }
        
        return None
    
    def parse_causal_sentence(self, sentence: str, source_info: Dict) -> Dict:
        """Разбор причинно-следственного предложения в правило"""
        if self.language == 'ru':
            patterns = [
                r'(.+?)\s+приводит к\s+(.+)',
                r'из-за\s+(.+?)\s+происходит\s+(.+)',
                r'(.+?)\s+вызывает\s+(.+)',
                r'вследствие\s+(.+?)\s+наступает\s+(.+)'
            ]
        else:
            patterns = [
                r'(.+?)\s+leads to\s+(.+)',
                r'due to\s+(.+?)\s+there is\s+(.+)',
                r'(.+?)\s+causes\s+(.+)',
                r'as a result of\s+(.+?)\s+we have\s+(.+)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                cause = match.group(1).strip().rstrip(',.')
                effect = match.group(2).strip().rstrip('.')
                
                return {
                    'name': f"Причинное правило из {source_info['source_file']}",
                    'condition': cause,
                    'action': effect,
                    'rule_type': 'causal',
                    'priority': 1,
                    'agent_id': source_info['agent_id'],
                    'source_file': source_info['source_file'],
                    'author': source_info['author']
                }
        
        return None
    
    def _parse_definition_sentence(self, sentence: str, source_info: Dict) -> Dict:
        """Разбор определения в факт"""
        if self.language == 'ru':
            patterns = [
                r'(.+?)\s+[—\-]\s+это\s+(.+)',
                r'(.+?)\s+это\s+(.+)',
                r'(.+?)\s+является\s+(.+)',
                r'(.+?)\s+называется\s+(.+)',
                r'(.+?)\s+означает\s+(.+)'
            ]
        else:
            patterns = [
                r'(.+?)\s+is\s+(.+)',
                r'(.+?)\s+means\s+(.+)',
                r'(.+?)\s+refers to\s+(.+)',
                r'(.+?)\s+is called\s+(.+)',
                r'(.+?)\s+is defined as\s+(.+)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
            if match:
                variable = match.group(1).strip()
                value = match.group(2).strip().rstrip('.')
                
                # Ограничиваем длину
                if len(variable) > 100 or len(value) > 500:
                    continue
                
                return {
                    'variable_name': variable,
                    'value': value,
                    'agent_id': source_info['agent_id'],
                    'source_file': source_info['source_file'],
                    'author': source_info['author'],
                    'confidence': 0.8
                }
        
        return None