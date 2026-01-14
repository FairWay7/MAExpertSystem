import re
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class SimpleTextProcessor:
    def __init__(self, language='ru'):
        self.language = language

        # Паттерны для извлечения в зависимости от языка
        if language == 'ru':
            self._init_russian_patterns()
        else:
            self._init_english_patterns()

    def _init_russian_patterns(self):
        """Инициализация паттернов для русского языка"""
        # Паттерны для правил
        self.rule_patterns = [
            # Если ... то ...
            (r'если\s+(.+?)\s*[,;]\s*(?:то|тогда)\s+(.+)', 'conditional', 1.0),
            # При ... происходит ...
            (r'при\s+(.+?)\s*[,;]\s*(?:происходит|наблюдается|возникает)\s+(.+)', 'conditional', 0.9),
            # Когда ... тогда ...
            (r'когда\s+(.+?)\s*[,;]\s*(?:тогда|то)\s+(.+)', 'conditional', 0.9),
            # X приводит к Y
            (r'(.+?)\s+приводит к\s+(.+)', 'causal', 0.8),
            # Из-за X наступает Y
            (r'из-за\s+(.+?)\s+наступает\s+(.+)', 'causal', 0.8),
        ]

        # Паттерны для фактов
        self.fact_patterns = [
            # X - это Y
            (r'([А-Я][А-Яа-яёЁ\s]{0,50}?)\s+[—\-]\s+это\s+(.+)', 0.95),
            # X это Y
            (r'([А-Я][А-Яа-яёЁ\s]{0,50}?)\s+это\s+(.+)', 0.9),
            # X является Y
            (r'([А-Я][А-Яа-яёЁ\s]{0,50}?)\s+является\s+(.+)', 0.9),
            # X = значение
            (r'([А-Яа-яёЁA-Za-z_]+)\s*[=:]\s*([0-9]+(?:\.[0-9]+)?|[А-Яа-яёЁA-Za-z_]+)', 0.85),
        ]

        # Паттерны для токенизации предложений
        self.sentence_endings = r'[.!?]+'

    def _init_english_patterns(self):
        """Инициализация паттернов для английского языка"""
        # Паттерны для правил
        self.rule_patterns = [
            # If ... then ...
            (r'if\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional', 1.0),
            # When ... then ...
            (r'when\s+(.+?)\s*[,;]\s*then\s+(.+)', 'conditional', 0.9),
            # In case of ... occurs ...
            (r'in case of\s+(.+?)\s*[,;]\s*occurs\s+(.+)', 'conditional', 0.8),
            # X leads to Y
            (r'(.+?)\s+leads to\s+(.+)', 'causal', 0.8),
            # X causes Y
            (r'(.+?)\s+causes\s+(.+)', 'causal', 0.8),
        ]

        # Паттерны для фактов
        self.fact_patterns = [
            # X is Y
            (r'([A-Z][A-Za-z\s]{0,50}?)\s+is\s+(.+)', 0.95),
            # X means Y
            (r'([A-Z][A-Za-z\s]{0,50}?)\s+means\s+(.+)', 0.9),
            # X refers to Y
            (r'([A-Z][A-Za-z\s]{0,50}?)\s+refers to\s+(.+)', 0.9),
            # X = value
            (r'([A-Za-z_]+)\s*[=:]\s*([0-9]+(?:\.[0-9]+)?|[A-Za-z_]+)', 0.85),
        ]

        # Паттерны для токенизации предложений
        self.sentence_endings = r'[.!?]+'

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Разбивает текст на предложения.
        Простая реализация без зависимостей.
        """
        if not text:
            return []

        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text.strip())

        # Разбиваем по знакам конца предложения
        raw_sentences = re.split(self.sentence_endings, text)

        # Очищаем и фильтруем предложения
        sentences = []
        for sent in raw_sentences:
            sent = sent.strip()
            if sent and len(sent) > 5:  # Пропускаем слишком короткие
                sentences.append(sent)

        return sentences

    def extract_rules_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение правил из текста"""
        rules = []

        # Безопасная обработка текста
        try:
            sentences = self.split_into_sentences(text)

            for sentence in sentences:
                rule = self._extract_rule_from_sentence(sentence, source_info)
                if rule:
                    rules.append(rule)
        except Exception as e:
            print(f"Ошибка при извлечении правил: {e}")

        return rules

    def _extract_rule_from_sentence(self, sentence: str, source_info: Dict) -> Optional[Dict]:
        """Извлечение правила из одного предложения"""
        for pattern, rule_type, confidence in self.rule_patterns:
            try:
                match = re.search(pattern, sentence, re.IGNORECASE | re.DOTALL)
                if match:
                    condition = self._clean_text(match.group(1))
                    action = self._clean_text(match.group(2))

                    # Пропускаем слишком короткие или слишком длинные
                    if len(condition) < 3 or len(action) < 3:
                        continue
                    if len(condition) > 500 or len(action) > 500:
                        continue

                    return {
                        'id': str(uuid.uuid4()),
                        'name': f"Правило из '{source_info['source_file']}'",
                        'condition': condition,
                        'action': action,
                        'rule_type': rule_type,
                        'priority': 1,
                        'agent_id': source_info.get('agent_id', 'default'),
                        'source_file': source_info['source_file'],
                        'author': source_info.get('author', 'system'),
                        'created_date': datetime.now(),
                        'confidence': confidence,
                        'tags': ['extracted'],
                        'metadata': {
                            'sentence': sentence[:200],
                            'pattern': pattern[:100]
                        }
                    }
            except Exception as e:
                # Пропускаем ошибки в отдельных паттернах
                continue

        return None

    def extract_facts_from_text(self, text: str, source_info: Dict) -> List[Dict]:
        """Извлечение фактов из текста"""
        facts = []

        try:
            # Ищем факты во всем тексте (не только по предложениям)
            for pattern, confidence in self.fact_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    try:
                        variable = self._clean_text(match.group(1))
                        value = self._clean_text(match.group(2))

                        # Пропускаем слишком короткие или слишком длинные
                        if len(variable) < 2 or len(value) < 2:
                            continue
                        if len(variable) > 100 or len(value) > 200:
                            continue

                        facts.append({
                            'id': str(uuid.uuid4()),
                            'variable_name': variable,
                            'value': value,
                            'agent_id': source_info.get('agent_id', 'default'),
                            'source_file': source_info['source_file'],
                            'author': source_info.get('author', 'system'),
                            'created_date': datetime.now(),
                            'confidence': confidence
                        })
                    except:
                        continue
        except Exception as e:
            print(f"Ошибка при извлечении фактов: {e}")

        return facts

    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних пробелов и символов"""
        if not text:
            return ""

        # Заменяем множественные пробелы на один
        text = re.sub(r'\s+', ' ', text)

        # Удаляем пробелы в начале и конце
        text = text.strip()

        # Удаляем лишние запятые и точки в конце
        text = re.sub(r'[.,;]+$', '', text)

        return text

    def analyze_text_structure(self, text: str) -> Dict:
        """Анализ структуры текста"""
        result = {
            'total_chars': len(text),
            'total_words': len(re.findall(r'\b\w+\b', text)) if text else 0,
            'sentences': len(self.split_into_sentences(text)),
            'potential_rules': 0,
            'potential_facts': 0,
        }

        # Быстрая оценка количества потенциальных правил и фактов
        sentences = self.split_into_sentences(text)
        for sentence in sentences[:100]:  # Ограничиваем для скорости
            for pattern, _, _ in self.rule_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    result['potential_rules'] += 1
                    break

        for pattern, _ in self.fact_patterns:
            result['potential_facts'] += len(re.findall(pattern, text, re.IGNORECASE))

        return result


# Фабрика для создания процессоров
def create_text_processor(use_simple=True, language='ru'):
    """
    Создает текстовый процессор.

    Args:
        use_simple: Если True, использует простую версию без зависимостей
        language: Язык текста ('ru' или 'en')

    Returns:
        Текстовый процессор
    """
    if use_simple:
        return SimpleTextProcessor(language)
    else:
        # Пробуем создать продвинутый процессор
        try:
            from text_processor_advanced import AdvancedTextProcessor
            return AdvancedTextProcessor(language)
        except:
            # Если не получилось, возвращаем простой
            return SimpleTextProcessor(language)