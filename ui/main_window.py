import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.advanced_text_processor import AdvancedTextProcessor
from ui.selection_widget import SelectionWidget
from ui.explanation_subsystem import ExplanationSubsystem
from ui.styles import APP_STYLES

from ui.main_window_handlers import (
    load_initial_data_impl, on_domain_changed_impl, on_agent_changed_impl,
    load_file_impl, save_text_impl, analyze_text_impl, show_rules_impl,
    show_facts_impl, new_domain_impl, new_agent_impl, show_about_impl,
    show_statistics_impl, close_event_impl
)
from ui.main_window_tables import (
    filter_rules_impl, refresh_rules_table_impl, refresh_facts_table_impl,
    delete_selected_rule_impl, edit_rule_priority_impl, delete_selected_fact_impl,
    edit_selected_fact_impl, search_rules_dialog_impl, search_facts_dialog_impl,
    search_by_variable_impl
)
from ui.main_window_analysis import (
    trace_agent_impl, compare_agents_impl
)
from ui.main_window_inference import (
    forward_inference_impl, backward_inference_impl
)
from ui.main_window_export import (
    export_data_impl, import_data_impl, export_data_csv_impl
)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        self.db_manager = DatabaseManager()
        self.text_processor = AdvancedTextProcessor(language='ru')
        self.explanation = ExplanationSubsystem()

        self.current_agent_id = None
        self.current_domain_id = None
        self.current_file_name = None
        self.all_rules = []

        self.init_ui()
        self.load_initial_data()

    def init_ui(self):
        self.setWindowTitle('Система анализа текста и управления базами знаний')
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(APP_STYLES)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.selection_widget = SelectionWidget(self.db_manager)
        self.selection_widget.domainChanged.connect(self.on_domain_changed)
        self.selection_widget.agentChanged.connect(self.on_agent_changed)
        self.selection_widget.new_domain_btn.clicked.connect(self.new_domain)
        self.selection_widget.new_agent_btn.clicked.connect(self.new_agent)
        main_layout.addWidget(self.selection_widget)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.create_left_panel(), 1)
        content_layout.addWidget(self.create_right_panel(), 3)
        main_layout.addLayout(content_layout)

        self.selection_widget.domainChanged.connect(self.on_domain_changed)
        self.selection_widget.agentChanged.connect(self.on_agent_changed)

        self.create_menu_bar()
        self.statusBar().showMessage('Готово')

    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # title_label = QLabel("УПРАВЛЕНИЕ")
        # title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        # layout.addWidget(title_label)

        # Группа загрузки и анализа
        analysis_group = QGroupBox("Анализ текста")
        analysis_layout = QVBoxLayout(analysis_group)

        load_btn = QPushButton("Загрузить файл")
        load_btn.clicked.connect(self.load_file)
        analysis_layout.addWidget(load_btn)

        analyze_btn = QPushButton("Анализировать текст")
        analyze_btn.clicked.connect(self.analyze_text)
        analysis_layout.addWidget(analyze_btn)
        layout.addWidget(analysis_group)

        # Группа просмотра
        view_group = QGroupBox("Просмотр")
        view_layout = QVBoxLayout(view_group)

        rules_btn = QPushButton("Просмотр правил")
        rules_btn.clicked.connect(self.show_rules)
        view_layout.addWidget(rules_btn)

        facts_btn = QPushButton("Просмотр фактов")
        facts_btn.clicked.connect(self.show_facts)
        view_layout.addWidget(facts_btn)
        layout.addWidget(view_group)

        # Группа анализа БЗ
        analysis_group2 = QGroupBox("Анализ БЗ")
        analysis2_layout = QVBoxLayout(analysis_group2)

        trace_btn = QPushButton("Трассировка агента")
        trace_btn.clicked.connect(self.trace_agent)
        analysis2_layout.addWidget(trace_btn)

        compare_btn = QPushButton("Сравнение агентов")
        compare_btn.clicked.connect(self.compare_agents)
        analysis2_layout.addWidget(compare_btn)

        search_btn = QPushButton("Поиск по переменным")
        search_btn.clicked.connect(self.search_by_variable)
        analysis2_layout.addWidget(search_btn)
        layout.addWidget(analysis_group2)

        # Группа вывода
        inference_group = QGroupBox("Механизм вывода")
        inference_layout = QVBoxLayout(inference_group)

        forward_btn = QPushButton("Прямой вывод")
        forward_btn.clicked.connect(self.forward_inference)
        inference_layout.addWidget(forward_btn)

        backward_btn = QPushButton("Обратный вывод")
        backward_btn.clicked.connect(self.backward_inference)
        inference_layout.addWidget(backward_btn)
        layout.addWidget(inference_group)

        # Группа управления
        manage_group = QGroupBox("Управление")
        manage_layout = QVBoxLayout(manage_group)

        new_domain_btn = QPushButton("Новая область")
        new_domain_btn.clicked.connect(self.new_domain)
        manage_layout.addWidget(new_domain_btn)

        new_agent_btn = QPushButton("Новый агент")
        new_agent_btn.clicked.connect(self.new_agent)
        manage_layout.addWidget(new_agent_btn)
        layout.addWidget(manage_group)

        layout.addStretch()
        return panel

    def create_right_panel(self) -> QWidget:
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setPlaceholderText(
            "Введите текст для анализа или загрузите файл...\n\n"
            "Пример:\n"
            "Если температура выше 38 градусов, то это лихорадка.\n"
            "Нормальная температура = 36.6 градусов.\n"
            "Если давление выше 140/90, то это гипертония."
        )
        self.tab_widget.addTab(self.text_edit, "Текст")

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.results_text, "Результаты")

        self.rules_widget = self.create_rules_widget()
        self.tab_widget.addTab(self.rules_widget, "Правила")

        self.facts_widget = self.create_facts_widget()
        self.tab_widget.addTab(self.facts_widget, "Факты")

        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.trace_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.trace_text, "Трассировка")

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.explanation_text, "Объяснение")

        return self.tab_widget

    def create_rules_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()

        self.refresh_rules_btn = QPushButton("Обновить")
        self.refresh_rules_btn.clicked.connect(self.refresh_rules_table)

        self.delete_rule_btn = QPushButton("Удалить")
        self.delete_rule_btn.clicked.connect(self.delete_selected_rule)

        self.edit_priority_btn = QPushButton("Приоритет")
        self.edit_priority_btn.clicked.connect(self.edit_rule_priority)

        self.search_rules_btn = QPushButton("Поиск")
        self.search_rules_btn.clicked.connect(self.search_rules_dialog)

        self.rules_search_edit = QLineEdit()
        self.rules_search_edit.setPlaceholderText("Поиск по правилам...")
        self.rules_search_edit.textChanged.connect(self.filter_rules)

        self.rules_type_filter = QComboBox()
        self.rules_type_filter.addItems(["Все типы", "conditional", "factual", "default"])
        self.rules_type_filter.currentTextChanged.connect(self.filter_rules)

        toolbar.addWidget(self.refresh_rules_btn)
        toolbar.addWidget(self.delete_rule_btn)
        toolbar.addWidget(self.edit_priority_btn)
        # toolbar.addWidget(self.search_rules_btn)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Поиск:"))
        toolbar.addWidget(self.rules_search_edit)
        toolbar.addWidget(QLabel("Тип:"))
        toolbar.addWidget(self.rules_type_filter)

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(8)
        self.rules_table.setHorizontalHeaderLabels([
            '', 'Название', 'Условие', 'Действие', 'Тип',
            'Приоритет', 'Агент', 'Дата'
        ])
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rules_table.setAlternatingRowColors(True)
        self.rules_table.setSortingEnabled(True)

        self.rules_table.setColumnWidth(0, 40)
        self.rules_table.setColumnWidth(1, 150)
        self.rules_table.setColumnWidth(2, 250)
        self.rules_table.setColumnWidth(3, 250)
        self.rules_table.setColumnWidth(4, 80)
        self.rules_table.setColumnWidth(5, 80)
        self.rules_table.setColumnWidth(6, 120)
        self.rules_table.setColumnWidth(7, 120)

        self.rules_status_label = QLabel()
        self.rules_status_label.setStyleSheet("color: #666; padding: 5px;")

        layout.addLayout(toolbar)
        layout.addWidget(self.rules_table)
        layout.addWidget(self.rules_status_label)

        return widget

    def create_facts_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()

        self.refresh_facts_btn = QPushButton("Обновить")
        self.refresh_facts_btn.clicked.connect(self.refresh_facts_table)

        self.delete_fact_btn = QPushButton("Удалить")
        self.delete_fact_btn.clicked.connect(self.delete_selected_fact)

        self.edit_fact_btn = QPushButton("Редактировать")
        self.edit_fact_btn.clicked.connect(self.edit_selected_fact)

        self.search_facts_btn = QPushButton("Поиск")
        self.search_facts_btn.clicked.connect(self.search_facts_dialog)

        toolbar.addWidget(self.refresh_facts_btn)
        toolbar.addWidget(self.delete_fact_btn)
        toolbar.addWidget(self.edit_fact_btn)
        toolbar.addWidget(self.search_facts_btn)
        toolbar.addStretch()

        self.facts_table = QTableWidget()
        self.facts_table.setColumnCount(6)
        self.facts_table.setHorizontalHeaderLabels([
            'ID', 'Переменная', 'Значение', 'Достоверность', 'Агент', 'Дата'
        ])
        self.facts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.facts_table.setAlternatingRowColors(True)

        self.facts_status_label = QLabel()
        self.facts_status_label.setStyleSheet("color: #666; padding: 5px;")

        layout.addLayout(toolbar)
        layout.addWidget(self.facts_table)
        layout.addWidget(self.facts_status_label)

        return widget

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')
        load_action = QAction('Загрузить файл', self)
        load_action.triggered.connect(self.load_file)
        load_action.setShortcut('Ctrl+O')
        file_menu.addAction(load_action)

        save_action = QAction('Сохранить текст', self)
        save_action.triggered.connect(self.save_text)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)

        kb_menu = menubar.addMenu('База знаний')
        new_domain_action = QAction('Новая предметная область', self)
        new_domain_action.triggered.connect(self.new_domain)
        kb_menu.addAction(new_domain_action)

        new_agent_action = QAction('Новый агент', self)
        new_agent_action.triggered.connect(self.new_agent)
        kb_menu.addAction(new_agent_action)

        kb_menu.addSeparator()
        export_action = QAction('Экспорт в JSON', self)
        export_action.triggered.connect(self.export_data)
        kb_menu.addAction(export_action)

        import_action = QAction('Импорт из JSON', self)
        import_action.triggered.connect(self.import_data)
        kb_menu.addAction(import_action)

        export_action_csv = QAction('Экспорт в CSV', self)
        export_action_csv.triggered.connect(self.export_data_csv)
        kb_menu.addAction(export_action_csv)

        analysis_menu = menubar.addMenu('Анализ')
        analyze_action = QAction('Анализировать текст', self)
        analyze_action.triggered.connect(self.analyze_text)
        analysis_menu.addAction(analyze_action)

        trace_action = QAction('Трассировка агента', self)
        trace_action.triggered.connect(self.trace_agent)
        analysis_menu.addAction(trace_action)

        compare_action = QAction('Сравнение агентов', self)
        compare_action.triggered.connect(self.compare_agents)
        analysis_menu.addAction(compare_action)

        inference_menu = menubar.addMenu('Вывод')
        forward_action = QAction('Прямой вывод', self)
        forward_action.triggered.connect(self.forward_inference)
        inference_menu.addAction(forward_action)

        backward_action = QAction('Обратный вывод', self)
        backward_action.triggered.connect(self.backward_inference)
        inference_menu.addAction(backward_action)

        help_menu = menubar.addMenu('Помощь')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        stats_action = QAction('Статистика', self)
        stats_action.triggered.connect(self.show_statistics)
        help_menu.addAction(stats_action)

    # Обертки для вызова имплементаций
    def load_initial_data(self):
        load_initial_data_impl(self)

    def on_domain_changed(self, domain_id: str):
        on_domain_changed_impl(self, domain_id)

    def on_agent_changed(self, agent_id: str):
        on_agent_changed_impl(self, agent_id)

    def load_file(self):
        load_file_impl(self)

    def save_text(self):
        save_text_impl(self)

    def analyze_text(self):
        analyze_text_impl(self)

    def show_rules(self):
        show_rules_impl(self)

    def show_facts(self):
        show_facts_impl(self)

    def new_domain(self):
        new_domain_impl(self)

    def new_agent(self):
        new_agent_impl(self)

    def show_about(self):
        show_about_impl(self)

    def show_statistics(self):
        show_statistics_impl(self)

    def closeEvent(self, event):
        close_event_impl(self, event)

    def filter_rules(self):
        filter_rules_impl(self)

    def refresh_rules_table(self, agent_id=None):
        refresh_rules_table_impl(self, agent_id)

    def refresh_facts_table(self, agent_id=None):
        refresh_facts_table_impl(self, agent_id)

    def delete_selected_rule(self):
        delete_selected_rule_impl(self)

    def edit_rule_priority(self):
        edit_rule_priority_impl(self)

    def delete_selected_fact(self):
        delete_selected_fact_impl(self)

    def edit_selected_fact(self):
        edit_selected_fact_impl(self)

    def search_rules_dialog(self):
        search_rules_dialog_impl(self)

    def search_facts_dialog(self):
        search_facts_dialog_impl(self)

    def search_by_variable(self):
        search_by_variable_impl(self)

    def trace_agent(self):
        trace_agent_impl(self)

    def compare_agents(self):
        compare_agents_impl(self)

    def forward_inference(self):
        forward_inference_impl(self)

    def backward_inference(self):
        backward_inference_impl(self)

    def export_data(self):
        export_data_impl(self)

    def import_data(self):
        import_data_impl(self)

    def export_data_csv(self):
        export_data_csv_impl(self)