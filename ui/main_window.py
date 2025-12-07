import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from core.text_processor import TextProcessor
from core.knowledge_base import KnowledgeBase
from core.inference_engine import InferenceEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_processor = TextProcessor()
        self.current_kb = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Система управления базами знаний')
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель - навигация
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Кнопки управления
        self.btn_new_domain = QPushButton('Новая предметная область')
        self.btn_load_file = QPushButton('Загрузить файл')
        self.btn_analyze = QPushButton('Анализировать текст')
        self.btn_view_rules = QPushButton('Просмотр правил')
        self.btn_trace_agent = QPushButton('Трассировка агента')
        self.btn_trace_multi = QPushButton('Сравнение агентов')
        self.btn_forward = QPushButton('Прямой вывод')
        self.btn_backward = QPushButton('Обратный вывод')

        left_layout.addWidget(self.btn_new_domain)
        left_layout.addWidget(self.btn_load_file)
        left_layout.addWidget(self.btn_analyze)
        left_layout.addWidget(QHLine())
        left_layout.addWidget(self.btn_view_rules)
        left_layout.addWidget(self.btn_trace_agent)
        left_layout.addWidget(self.btn_trace_multi)
        left_layout.addWidget(QHLine())
        left_layout.addWidget(self.btn_forward)
        left_layout.addWidget(self.btn_backward)
        left_layout.addStretch()

        # Правая панель - рабочая область
        self.tab_widget = QTabWidget()

        # Вкладка текстового редактора
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 10))
        self.tab_widget.addTab(self.text_edit, "Текст")

        # Вкладка результатов анализа
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.tab_widget.addTab(self.results_text, "Результаты")

        # Вкладка базы знаний
        self.kb_table = QTableWidget()
        self.kb_table.setColumnCount(6)
        self.kb_table.setHorizontalHeaderLabels(['ID', 'Правило', 'Условие', 'Действие', 'Агент', 'Приоритет'])
        self.tab_widget.addTab(self.kb_table, "База знаний")

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.tab_widget, 3)

        # Подключение сигналов
        self.btn_load_file.clicked.connect(self.load_file)
        self.btn_analyze.clicked.connect(self.analyze_text)
        # self.btn_view_rules.clicked.connect(self.view_rules)

        # Статус бар
        self.statusBar().showMessage('Готово')

    def load_file(self):
        """Загрузка файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
                self.text_edit.setText(text)
                self.statusBar().showMessage(f'Загружен файл: {filename}')

    def analyze_text(self):
        """Анализ текста и извлечение знаний"""
        text = self.text_edit.toPlainText()

        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет текста для анализа")
            return

        # Создаем или получаем базу знаний
        if not self.current_kb:
            self.current_kb = KnowledgeBase("Новая область")

        source_info = {
            'agent_id': 'expert_1',
            'source_file': 'manual.txt',
            'author': 'Система'
        }

        # Извлекаем правила
        rules = self.text_processor.extract_rules_from_text(text, source_info)

        # Извлекаем факты
        facts = self.text_processor.extract_facts_from_text(text, source_info)

        # Добавляем в базу знаний
        for rule_data in rules:
            self.current_kb.add_rule(rule_data)

        for fact_data in facts:
            self.current_kb.add_fact(fact_data)

        # Показываем результаты
        result_text = f"Извлечено правил: {len(rules)}\n"
        result_text += f"Извлечено фактов: {len(facts)}\n\n"

        result_text += "=== ПРАВИЛА ===\n"
        for rule in rules:
            result_text += f"• {rule['condition']} → {rule['action']}\n"

        result_text += "\n=== ФАКТЫ ===\n"
        for fact in facts:
            result_text += f"• {fact['variable_name']} = {fact['value']}\n"

        self.results_text.setText(result_text)
        self.statusBar().showMessage(f'Анализ завершен. Извлечено {len(rules)} правил и {len(facts)} фактов')


class QHLine(QFrame):
    """Горизонтальная линия"""

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)