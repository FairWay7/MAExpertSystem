import re
import sys
import os
from typing import List, Dict, Optional

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.text_processor import TextProcessor


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        # Инициализация менеджера БД
        self.db_manager = DatabaseManager()

        # Инициализация текстового процессора
        self.text_processor = TextProcessor(language='ru')

        # Текущие данные
        self.current_agent_id = None
        self.current_domain_id = None

        # Инициализация UI
        self.init_ui()

        # Загрузка начальных данных
        self.load_initial_data()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Система анализа текста и управления базами знаний')
        self.setGeometry(100, 100, 1200, 800)

        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QHBoxLayout(central_widget)

        # Левая панель - навигация
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Правая панель - рабочая область
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)

        # Создание меню
        self.create_menu_bar()

        # Статус бар
        self.statusBar().showMessage('Готово')

    def create_left_panel(self) -> QWidget:
        """Создание левой панели навигации"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Кнопки управления
        buttons = [
            ('Загрузить файл', self.load_file),
            ('Анализировать текст', self.analyze_text),
            ('Просмотр правил', self.show_rules),
            ('Просмотр фактов', self.show_facts),
            ('Трассировка агента', self.trace_agent),
            ('Сравнение агентов', self.compare_agents),
            ('Прямой вывод', self.forward_inference),
            ('Обратный вывод', self.backward_inference),
            ('Новая область', self.new_domain),
            ('Новый агент', self.new_agent)
        ]

        for text, slot in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    font-size: 14px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()
        return panel

    def create_right_panel(self) -> QWidget:
        """Создание правой панели с вкладками"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Вкладка 1: Текстовый редактор
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 11))
        self.text_edit.setPlaceholderText(
            "Введите текст для анализа или загрузите файл...\n\nПример:\nЕсли температура выше 38 градусов, то это лихорадка.\nНормальная температура = 36.6 градусов.\nЕсли давление выше 140/90, то это гипертония.")
        self.tab_widget.addTab(self.text_edit, "Текст")

        # Вкладка 2: Результаты анализа
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 10))
        self.tab_widget.addTab(self.results_text, "Результаты")

        # Вкладка 3: Правила
        self.rules_widget = self.create_rules_widget()
        self.tab_widget.addTab(self.rules_widget, "Правила")

        # Вкладка 4: Факты
        self.facts_widget = self.create_facts_widget()
        self.tab_widget.addTab(self.facts_widget, "Факты")

        # Вкладка 5: Трассировка
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.trace_text.setFont(QFont("Courier", 10))
        self.tab_widget.addTab(self.trace_text, "Трассировка")

        return self.tab_widget

    def create_rules_widget(self) -> QWidget:
        """Создание виджета для отображения правил"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Панель инструментов
        toolbar = QHBoxLayout()

        self.refresh_rules_btn = QPushButton("Обновить")
        self.refresh_rules_btn.clicked.connect(self.refresh_rules_table)

        self.delete_rule_btn = QPushButton("Удалить")
        self.delete_rule_btn.clicked.connect(self.delete_selected_rule)

        self.edit_priority_btn = QPushButton("Изменить приоритет")
        self.edit_priority_btn.clicked.connect(self.edit_rule_priority)

        toolbar.addWidget(self.refresh_rules_btn)
        toolbar.addWidget(self.delete_rule_btn)
        toolbar.addWidget(self.edit_priority_btn)
        toolbar.addStretch()

        # Таблица правил
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(8)
        self.rules_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Условие', 'Действие', 'Тип',
            'Приоритет', 'Агент', 'Дата'
        ])
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rules_table.setAlternatingRowColors(True)

        layout.addLayout(toolbar)
        layout.addWidget(self.rules_table)

        return widget

    def create_facts_widget(self) -> QWidget:
        """Создание виджета для отображения фактов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Таблица фактов
        self.facts_table = QTableWidget()
        self.facts_table.setColumnCount(6)
        self.facts_table.setHorizontalHeaderLabels([
            'ID', 'Переменная', 'Значение', 'Достоверность', 'Агент', 'Дата'
        ])
        self.facts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.facts_table.setAlternatingRowColors(True)

        layout.addWidget(self.facts_table)

        return widget

    def create_menu_bar(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        load_action = QAction('Загрузить файл', self)
        load_action.triggered.connect(self.load_file)
        file_menu.addAction(load_action)

        save_action = QAction('Сохранить текст', self)
        save_action.triggered.connect(self.save_text)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню База знаний
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

        # Меню Анализ
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

        # Меню Вывод
        inference_menu = menubar.addMenu('Вывод')

        forward_action = QAction('Прямой вывод', self)
        forward_action.triggered.connect(self.forward_inference)
        inference_menu.addAction(forward_action)

        backward_action = QAction('Обратный вывод', self)
        backward_action.triggered.connect(self.backward_inference)
        inference_menu.addAction(backward_action)

        # Меню Помощь
        help_menu = menubar.addMenu('Помощь')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        stats_action = QAction('Статистика', self)
        stats_action.triggered.connect(self.show_statistics)
        help_menu.addAction(stats_action)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        # Проверяем наличие стандартного домена
        domains = self.db_manager.get_all_domains()

        if not domains:
            # Создаем стандартный домен
            default_domain = self.db_manager.create_domain(
                name="Общая предметная область",
                description="Автоматически созданный домен"
            )
            if default_domain:
                self.current_domain_id = default_domain['id']

        # Проверяем наличие стандартного агента
        agents = self.db_manager.get_all_agents()

        if not agents:
            # Создаем стандартного агента
            default_agent = self.db_manager.create_agent(
                name="Системный эксперт",
                domain_id=self.current_domain_id,
                description="Агент по умолчанию"
            )
            if default_agent:
                self.current_agent_id = default_agent['id']

        # Загружаем правила и факты
        self.refresh_rules_table()
        self.refresh_facts_table()

    # ===== Обработчики событий =====

    def load_file(self):
        """Загрузка текстового файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.text_edit.setText(text)
                    self.statusBar().showMessage(f'Загружен файл: {filename}')
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось загрузить файл:\n{str(e)}")

    def save_text(self):
        """Сохранение текста в файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить текст", "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.statusBar().showMessage(f'Текст сохранен в: {filename}')
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось сохранить файл:\n{str(e)}")

    def analyze_text(self):
        """Анализ текста и извлечение знаний"""
        text = self.text_edit.toPlainText()

        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет текста для анализа")
            return

        try:
            # Выбор агента для сохранения
            agent_id = self.select_agent_for_saving()
            if not agent_id:
                return

            # Получаем информацию об агенте
            agent = self.db_manager.get_agent(agent_id)
            domain_id = agent.get('domain_id') if agent else None

            # Подготавливаем информацию об источнике
            source_info = {
                'agent_id': agent_id,
                'domain_id': domain_id,
                'source_file': 'text_input.txt',
                'author': 'Пользователь'
            }

            # Анализируем структуру текста
            structure = self.text_processor.analyze_text_structure(text)

            # Извлекаем знания
            extracted_data = self.text_processor.extract_from_text(text, source_info)

            # Сохраняем правила в БД
            saved_rules = []
            for rule_data in extracted_data['rules']:
                saved_rule = self.db_manager.save_rule(rule_data)
                if saved_rule:
                    saved_rules.append(saved_rule)

            # Сохраняем факты в БД
            saved_facts = []
            for fact_data in extracted_data['facts']:
                saved_fact = self.db_manager.save_fact(fact_data)
                if saved_fact:
                    saved_facts.append(saved_fact)

            # Формируем отчет
            report = self.create_analysis_report(
                structure, extracted_data, saved_rules, saved_facts
            )

            # Отображаем результаты
            self.results_text.setText(report)
            self.tab_widget.setCurrentIndex(1)  # Переключаемся на вкладку результатов

            # Обновляем таблицы
            self.refresh_rules_table()
            self.refresh_facts_table()

            self.statusBar().showMessage(
                f'Анализ завершен. Сохранено {len(saved_rules)} правил и {len(saved_facts)} фактов'
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка анализа",
                                 f"Произошла ошибка при анализе текста:\n{str(e)}")

    def select_agent_for_saving(self) -> Optional[str]:
        """Выбор агента для сохранения результатов"""
        agents = self.db_manager.get_all_agents()

        if not agents:
            # Создаем нового агента
            agent_name, ok = QInputDialog.getText(
                self, "Новый агент", "Введите имя нового агента:"
            )

            if ok and agent_name:
                # Получаем первый домен
                domains = self.db_manager.get_all_domains()
                domain_id = domains[0]['id'] if domains else None

                agent = self.db_manager.create_agent(
                    name=agent_name,
                    domain_id=domain_id
                )

                if agent:
                    self.current_agent_id = agent['id']
                    return agent['id']

            return None

        elif len(agents) == 1:
            # Если агент только один, используем его
            self.current_agent_id = agents[0]['id']
            return agents[0]['id']

        else:
            # Показываем диалог выбора
            dialog = QDialog(self)
            dialog.setWindowTitle("Выбор агента")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Выберите агента для сохранения результатов:"))

            list_widget = QListWidget()
            for agent in agents:
                item = QListWidgetItem(agent['name'])
                item.setData(Qt.UserRole, agent['id'])
                list_widget.addItem(item)

            layout.addWidget(list_widget)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            if dialog.exec_() == QDialog.Accepted:
                selected_items = list_widget.selectedItems()
                if selected_items:
                    agent_id = selected_items[0].data(Qt.UserRole)
                    self.current_agent_id = agent_id
                    return agent_id

            return None

    def create_analysis_report(self, structure: Dict, extracted_data: Dict,
                               saved_rules: List, saved_facts: List) -> str:
        """Создание отчета об анализе"""
        report = "=" * 70 + "\n"
        report += "ОТЧЕТ ОБ АНАЛИЗЕ ТЕКСТА\n"
        report += "=" * 70 + "\n\n"

        # Статистика текста
        report += "СТАТИСТИКА ТЕКСТА:\n"
        report += f"  Символов: {structure['total_chars']}\n"
        report += f"  Слов: {structure['total_words']}\n"
        report += f"  Предложений: {structure['sentences']}\n"
        report += f"  Потенциальных правил: {structure['potential_rules']}\n"
        report += f"  Потенциальных фактов: {structure['potential_facts']}\n\n"

        # Результаты извлечения
        report += "РЕЗУЛЬТАТЫ ИЗВЛЕЧЕНИЯ:\n"
        report += f"  Найдено правил: {len(extracted_data['rules'])}\n"
        report += f"  Сохранено правил: {len(saved_rules)}\n"
        report += f"  Найдено фактов: {len(extracted_data['facts'])}\n"
        report += f"  Сохранено фактов: {len(saved_facts)}\n\n"

        if saved_rules:
            report += "СОХРАНЕННЫЕ ПРАВИЛА:\n"
            for i, rule in enumerate(saved_rules, 1):
                report += f"{i}. {rule['name']}\n"
                report += f"   ЕСЛИ: {rule['condition']}\n"
                report += f"   ТО: {rule['action']}\n"
                report += f"   Тип: {rule['rule_type']}, Приоритет: {rule['priority']}\n\n"

        if saved_facts:
            report += "СОХРАНЕННЫЕ ФАКТЫ:\n"
            for i, fact in enumerate(saved_facts, 1):
                report += f"{i}. {fact['variable_name']} = {fact['value']}\n"
                report += f"   Достоверность: {fact['confidence']:.2f}\n\n"

        report += "=" * 70

        return report

    def refresh_rules_table(self):
        """Обновление таблицы правил"""
        try:
            rules = self.db_manager.get_all_rules()

            self.rules_table.setRowCount(len(rules))

            for row, rule in enumerate(rules):
                # ID (укороченный)
                self.rules_table.setItem(row, 0,
                                         QTableWidgetItem(rule['id'][:8] + '...'))

                # Название
                self.rules_table.setItem(row, 1,
                                         QTableWidgetItem(rule.get('name', '')))

                # Условие
                self.rules_table.setItem(row, 2,
                                         QTableWidgetItem(rule['condition']))

                # Действие
                self.rules_table.setItem(row, 3,
                                         QTableWidgetItem(rule['action']))

                # Тип
                self.rules_table.setItem(row, 4,
                                         QTableWidgetItem(rule.get('rule_type', 'conditional')))

                # Приоритет
                self.rules_table.setItem(row, 5,
                                         QTableWidgetItem(str(rule.get('priority', 1))))

                # Агент (получаем имя)
                agent_id = rule.get('agent_id')
                agent_name = ""
                if agent_id:
                    agent = self.db_manager.get_agent(agent_id)
                    agent_name = agent['name'] if agent else agent_id
                self.rules_table.setItem(row, 6, QTableWidgetItem(agent_name))

                # Дата
                created_at = rule.get('created_at', '')
                if created_at:
                    # Пытаемся отформатировать дату
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = created_at[:19]
                else:
                    date_str = ''
                self.rules_table.setItem(row, 7, QTableWidgetItem(date_str))

            # Автоматическое изменение ширины столбцов
            self.rules_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка обновления таблицы правил: {e}")

    def refresh_facts_table(self):
        """Обновление таблицы фактов"""
        try:
            facts = self.db_manager.get_all_facts()

            self.facts_table.setRowCount(len(facts))

            for row, fact in enumerate(facts):
                # ID (укороченный)
                self.facts_table.setItem(row, 0,
                                         QTableWidgetItem(fact['id'][:8] + '...'))

                # Переменная
                self.facts_table.setItem(row, 1,
                                         QTableWidgetItem(fact['variable_name']))

                # Значение
                self.facts_table.setItem(row, 2,
                                         QTableWidgetItem(str(fact['value'])))

                # Достоверность
                confidence = fact.get('confidence', 1.0)
                self.facts_table.setItem(row, 3,
                                         QTableWidgetItem(f"{confidence:.2f}"))

                # Агент
                agent_id = fact.get('agent_id')
                agent_name = ""
                if agent_id:
                    agent = self.db_manager.get_agent(agent_id)
                    agent_name = agent['name'] if agent else agent_id
                self.facts_table.setItem(row, 4, QTableWidgetItem(agent_name))

                # Дата
                created_at = fact.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = created_at[:19]
                else:
                    date_str = ''
                self.facts_table.setItem(row, 5, QTableWidgetItem(date_str))

            # Автоматическое изменение ширины столбцов
            self.facts_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка обновления таблицы фактов: {e}")

    def show_rules(self):
        """Показать вкладку с правилами"""
        self.refresh_rules_table()
        self.tab_widget.setCurrentIndex(2)
        self.statusBar().showMessage("Отображены все правила")

    def show_facts(self):
        """Показать вкладку с фактами"""
        self.refresh_facts_table()
        self.tab_widget.setCurrentIndex(3)
        self.statusBar().showMessage("Отображены все факты")

    def delete_selected_rule(self):
        """Удаление выбранного правила"""
        selected_rows = self.rules_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите правило для удаления")
            return

        # Подтверждение удаления
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить выбранное правило?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                rule_id_item = self.rules_table.item(row, 0)

                if rule_id_item:
                    # Получаем полный ID (нужно хранить полные ID в таблице)
                    # В реальном приложении нужно хранить полные ID в данных ячеек
                    rules = self.db_manager.get_all_rules()
                    if row < len(rules):
                        rule_id = rules[row]['id']
                        self.db_manager.delete_rule(rule_id)

            # Обновляем таблицу
            self.refresh_rules_table()
            self.statusBar().showMessage("Правило удалено")

    def edit_rule_priority(self):
        """Изменение приоритета правила"""
        selected_rows = self.rules_table.selectionModel().selectedRows()

        if not selected_rows or len(selected_rows) > 1:
            QMessageBox.warning(self, "Ошибка",
                                "Выберите одно правило для изменения приоритета")
            return

        row = selected_rows[0].row()
        rules = self.db_manager.get_all_rules()

        if row >= len(rules):
            return

        rule = rules[row]

        # Диалог ввода нового приоритета
        priority, ok = QInputDialog.getInt(
            self, "Изменение приоритета",
            f"Введите новый приоритет для правила:\n{rule['condition']}",
            value=rule.get('priority', 1),
            min=1, max=10, step=1
        )

        if ok:
            success = self.db_manager.update_rule_priority(rule['id'], priority)
            if success:
                self.refresh_rules_table()
                self.statusBar().showMessage(f"Приоритет изменен на {priority}")
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Не удалось изменить приоритет")

    def trace_agent(self):
        """Трассировка агента"""
        agents = self.db_manager.get_all_agents()

        if not agents:
            QMessageBox.information(self, "Информация", "Нет доступных агентов")
            return

        # Диалог выбора агента
        agent_names = [agent['name'] for agent in agents]
        agent_name, ok = QInputDialog.getItem(
            self, "Выбор агента", "Выберите агента для трассировки:",
            agent_names, 0, False
        )

        if ok and agent_name:
            # Находим ID агента
            agent_id = None
            for agent in agents:
                if agent['name'] == agent_name:
                    agent_id = agent['id']
                    break

            if agent_id:
                # Получаем правила агента
                agent_rules = self.db_manager.get_rules_by_agent(agent_id)

                # Ищем схожие правила
                similar_rules = self.db_manager.find_similar_rules(agent_id)

                # Ищем конфликтные правила
                conflicting_rules = self.db_manager.find_conflicting_rules(agent_id)

                # Формируем отчет
                report = self.create_trace_report(
                    agent_name, agent_rules, similar_rules, conflicting_rules
                )

                # Отображаем отчет
                self.trace_text.setText(report)
                self.tab_widget.setCurrentIndex(4)  # Вкладка трассировки

                self.statusBar().showMessage(f"Выполнена трассировка агента: {agent_name}")

    def create_trace_report(self, agent_name: str, agent_rules: List,
                            similar_rules: List, conflicting_rules: List) -> str:
        """Создание отчета трассировки"""
        report = "=" * 70 + "\n"
        report += f"ОТЧЕТ ТРАССИРОВКИ АГЕНТА: {agent_name}\n"
        report += "=" * 70 + "\n\n"

        # Статистика
        report += "СТАТИСТИКА:\n"
        report += f"  Всего правил: {len(agent_rules)}\n"
        report += f"  Схожих пар правил: {len(similar_rules)}\n"
        report += f"  Конфликтных пар: {len(conflicting_rules)}\n\n"

        if similar_rules:
            report += "СХОЖИЕ ПРАВИЛА:\n"
            report += "-" * 40 + "\n"

            for i, pair in enumerate(similar_rules, 1):
                report += f"{i}. Степень схожести: {pair['similarity']:.2%}\n"
                report += f"   Правило 1: ЕСЛИ {pair['rule1']['condition']}\n"
                report += f"             ТО {pair['rule1']['action']}\n"
                report += f"   Правило 2: ЕСЛИ {pair['rule2']['condition']}\n"
                report += f"             ТО {pair['rule2']['action']}\n"
                report += f"   Тип схожести: {pair['type']}\n\n"

        if conflicting_rules:
            report += "\nКОНФЛИКТНЫЕ ПРАВИЛА:\n"
            report += "-" * 40 + "\n"

            for i, conflict in enumerate(conflicting_rules, 1):
                report += f"{i}. Тип конфликта: {conflict['conflict_type']}\n"
                report += f"   Схожесть условий: {conflict['condition_similarity']:.2%}\n"
                report += f"   Правило 1: ЕСЛИ {conflict['rule1']['condition']}\n"
                report += f"             ТО {conflict['rule1']['action']}\n"
                report += f"   Правило 2: ЕСЛИ {conflict['rule2']['condition']}\n"
                report += f"             ТО {conflict['rule2']['action']}\n\n"

        # Рекомендации
        report += "\nРЕКОМЕНДАЦИИ:\n"
        report += "-" * 40 + "\n"

        if similar_rules:
            report += "• Рассмотрите возможность объединения схожих правил\n"

        if conflicting_rules:
            report += "• Разрешите конфликты путем изменения приоритетов или условий\n"

        if len(agent_rules) < 5:
            report += "• База знаний мала. Добавьте больше правил\n"
        elif len(agent_rules) > 50:
            report += "• База знаний велика. Рассмотрите возможность оптимизации\n"

        report += "\n" + "=" * 70

        return report

    def compare_agents(self):
        """Сравнение нескольких агентов"""
        agents = self.db_manager.get_all_agents()

        if len(agents) < 2:
            QMessageBox.information(self, "Информация",
                                    "Для сравнения необходимо минимум 2 агента")
            return

        # Диалог выбора агентов
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор агентов для сравнения")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Выберите агентов для сравнения:"))

        self.agent_checkboxes = []
        for agent in agents:
            cb = QCheckBox(agent['name'])
            cb.agent_id = agent['id']  # Сохраняем ID в объекте чекбокса
            self.agent_checkboxes.append(cb)
            layout.addWidget(cb)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            selected_agents = []
            for cb in self.agent_checkboxes:
                if cb.isChecked():
                    selected_agents.append({
                        'id': cb.agent_id,
                        'name': cb.text()
                    })

            if len(selected_agents) < 2:
                QMessageBox.warning(self, "Ошибка", "Выберите минимум 2 агента")
                return

            # Сравниваем агентов
            comparison_report = self.create_comparison_report(selected_agents)

            # Отображаем отчет
            self.trace_text.setText(comparison_report)
            self.tab_widget.setCurrentIndex(4)

            self.statusBar().showMessage(f"Сравнение {len(selected_agents)} агентов")

    def create_comparison_report(self, agents: List[Dict]) -> str:
        """Создание отчета сравнения агентов"""
        report = "=" * 70 + "\n"
        report += "СРАВНЕНИЕ АГЕНТОВ\n"
        report += "=" * 70 + "\n\n"

        # Собираем данные по каждому агенту
        agents_data = []

        for agent in agents:
            rules = self.db_manager.get_rules_by_agent(agent['id'])
            facts = self.db_manager.get_facts_by_agent(agent['id'])

            agents_data.append({
                'name': agent['name'],
                'rules_count': len(rules),
                'facts_count': len(facts),
                'rules': rules,
                'facts': facts
            })

        # Отчет по каждому агенту
        for data in agents_data:
            report += f"АГЕНТ: {data['name']}\n"
            report += f"  Правил: {data['rules_count']}\n"
            report += f"  Фактов: {data['facts_count']}\n"

            # Анализ типов правил
            rule_types = {}
            for rule in data['rules']:
                rule_type = rule.get('rule_type', 'unknown')
                rule_types[rule_type] = rule_types.get(rule_type, 0) + 1

            if rule_types:
                report += "  Типы правил:\n"
                for rule_type, count in rule_types.items():
                    report += f"    • {rule_type}: {count}\n"

            report += "\n"

        # Сравнительный анализ
        report += "СРАВНИТЕЛЬНЫЙ АНАЛИЗ:\n"
        report += "-" * 40 + "\n"

        # Находим агента с наибольшим количеством правил
        max_rules_agent = max(agents_data, key=lambda x: x['rules_count'])
        min_rules_agent = min(agents_data, key=lambda x: x['rules_count'])

        report += f"• Наибольшее количество правил: {max_rules_agent['name']} "
        report += f"({max_rules_agent['rules_count']})\n"

        report += f"• Наименьшее количество правил: {min_rules_agent['name']} "
        report += f"({min_rules_agent['rules_count']})\n"

        # Разница в количестве
        diff = max_rules_agent['rules_count'] - min_rules_agent['rules_count']
        if diff > 0:
            report += f"• Разница: {diff} правил\n"

        report += "\nРЕКОМЕНДАЦИИ:\n"
        report += "-" * 40 + "\n"

        if diff > 10:
            report += "• Значительная разница в количестве правил. "
            report += "Рассмотрите возможность обмена знаниями между агентами\n"

        # Проверяем на дублирование правил между агентами
        all_rules = []
        for data in agents_data:
            all_rules.extend(data['rules'])

        # Ищем дубликаты между агентами
        rule_texts = {}
        duplicates = []

        for rule in all_rules:
            key = f"{rule['condition']}|{rule['action']}"
            if key in rule_texts:
                duplicates.append((rule_texts[key], rule))
            else:
                rule_texts[key] = rule

        if duplicates:
            report += f"• Обнаружено {len(duplicates)} дубликатов правил между агентами\n"

        report += "\n" + "=" * 70

        return report

    def forward_inference(self):
        """Прямой вывод"""
        # Диалог выбора начальных фактов
        dialog = QDialog(self)
        dialog.setWindowTitle("Прямой вывод")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Введите начальные факты (каждый с новой строки):"))

        facts_edit = QTextEdit()
        facts_edit.setPlainText("температура = 39.5\nдавление = 150/95")
        layout.addWidget(facts_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            # Парсим факты
            facts_text = facts_edit.toPlainText()
            initial_facts = []

            for line in facts_text.split('\n'):
                line = line.strip()
                if line:
                    parts = line.split('=')
                    if len(parts) == 2:
                        initial_facts.append({
                            'variable': parts[0].strip(),
                            'value': parts[1].strip()
                        })

            # Получаем все правила
            rules = self.db_manager.get_all_rules()

            # Простой алгоритм прямого вывода
            result = self.simple_forward_chaining(initial_facts, rules)

            # Отображаем результат
            report = self.create_inference_report("Прямой вывод",
                                                  initial_facts, rules, result)

            self.trace_text.setText(report)
            self.tab_widget.setCurrentIndex(4)

            self.statusBar().showMessage("Прямой вывод выполнен")

    def simple_forward_chaining(self, initial_facts: List, rules: List) -> Dict:
        """Простой алгоритм прямого вывода"""
        # Создаем рабочую память
        working_memory = {}
        for fact in initial_facts:
            working_memory[fact['variable']] = fact['value']

        applied_rules = []
        new_facts = []

        # Сортируем правила по приоритету
        sorted_rules = sorted(rules, key=lambda x: x.get('priority', 1), reverse=True)

        # Цикл вывода
        changed = True
        while changed:
            changed = False

            for rule in sorted_rules:
                # Проверяем, сработало ли правило
                if self.check_rule_condition(rule['condition'], working_memory):
                    # Извлекаем действие
                    action_result = self.execute_rule_action(rule['action'], working_memory)

                    if action_result:
                        variable, value = action_result

                        # Добавляем новый факт
                        if variable not in working_memory:
                            working_memory[variable] = value
                            new_facts.append({
                                'variable': variable,
                                'value': value,
                                'rule': rule['name']
                            })
                            applied_rules.append(rule['name'])
                            changed = True

        return {
            'final_facts': working_memory,
            'applied_rules': applied_rules,
            'new_facts': new_facts
        }

    def check_rule_condition(self, condition: str, facts: Dict) -> bool:
        """Проверка условия правила"""
        # Простая проверка для демонстрации
        # В реальном приложении нужен полноценный парсер условий

        try:
            # Заменяем переменные на их значения
            expr = condition
            for var, value in facts.items():
                expr = expr.replace(var, str(value))

            # Вычисляем выражение
            return eval(expr)
        except:
            return False

    def execute_rule_action(self, action: str, facts: Dict) -> Optional[tuple]:
        """Выполнение действия правила"""
        # Простой парсер для действий вида "переменная = значение"
        match = re.match(r'([\w]+)\s*=\s*(.+)', action)
        if match:
            variable = match.group(1)
            value_expr = match.group(2)

            try:
                # Заменяем переменные в выражении значения
                for var, val in facts.items():
                    value_expr = value_expr.replace(var, str(val))

                # Вычисляем значение
                value = eval(value_expr)
                return (variable, value)
            except:
                return None

        return None

    def create_inference_report(self, inference_type: str, initial_facts: List,
                                rules: List, result: Dict) -> str:
        """Создание отчета о выводе"""
        report = "=" * 70 + "\n"
        report += f"ОТЧЕТ О ВЫВОДЕ: {inference_type}\n"
        report += "=" * 70 + "\n\n"

        report += "НАЧАЛЬНЫЕ ФАКТЫ:\n"
        for fact in initial_facts:
            report += f"  • {fact['variable']} = {fact['value']}\n"

        report += f"\nВСЕГО ПРАВИЛ: {len(rules)}\n\n"

        if result['applied_rules']:
            report += "ПРИМЕНЕННЫЕ ПРАВИЛА:\n"
            for i, rule_name in enumerate(result['applied_rules'], 1):
                report += f"  {i}. {rule_name}\n"

        if result['new_facts']:
            report += "\nНОВЫЕ ФАКТЫ:\n"
            for fact in result['new_facts']:
                report += f"  • {fact['variable']} = {fact['value']} "
                report += f"(из правила: {fact['rule']})\n"

        report += "\nИТОГОВАЯ РАБОЧАЯ ПАМЯТЬ:\n"
        for var, value in result['final_facts'].items():
            report += f"  • {var} = {value}\n"

        report += "\n" + "=" * 70

        return report

    def backward_inference(self):
        """Обратный вывод"""
        # Диалог ввода цели
        goal, ok = QInputDialog.getText(
            self, "Обратный вывод",
            "Введите цель для доказательства (например, 'диагноз'):"
        )

        if ok and goal:
            # Простой алгоритм обратного вывода для демонстрации
            report = self.create_backward_inference_report(goal)

            self.trace_text.setText(report)
            self.tab_widget.setCurrentIndex(4)

            self.statusBar().showMessage(f"Обратный вывод для цели: {goal}")

    def create_backward_inference_report(self, goal: str) -> str:
        """Создание отчета обратного вывода"""
        report = "=" * 70 + "\n"
        report += f"ОБРАТНЫЙ ВЫВОД: доказать '{goal}'\n"
        report += "=" * 70 + "\n\n"

        # Получаем все правила
        rules = self.db_manager.get_all_rules()

        # Ищем правила, которые выводят цель
        relevant_rules = []
        for rule in rules:
            # Простая проверка: содержится ли цель в действии
            if goal.lower() in rule['action'].lower():
                relevant_rules.append(rule)

        if not relevant_rules:
            report += f"Не найдено правил, выводящих '{goal}'\n"
        else:
            report += f"Найдено правил, выводящих '{goal}': {len(relevant_rules)}\n\n"

            for i, rule in enumerate(relevant_rules, 1):
                report += f"ПРАВИЛО {i}:\n"
                report += f"  ЕСЛИ: {rule['condition']}\n"
                report += f"  ТО: {rule['action']}\n"
                report += f"  Приоритет: {rule.get('priority', 1)}\n"

                # Анализ условий
                report += f"  Условия для доказательства:\n"

                # Простой парсинг условий
                conditions = self.extract_conditions(rule['condition'])
                for cond in conditions:
                    report += f"    • {cond}\n"

                report += "\n"

        report += "\nПЛАН ДОКАЗАТЕЛЬСТВА:\n"
        report += "-" * 40 + "\n"

        if relevant_rules:
            report += "1. Выбрать правило с наивысшим приоритетом\n"
            report += "2. Доказать условия выбранного правила\n"
            report += "3. Если условия доказаны, цель считается доказанной\n"
            report += "4. Если условия не доказаны, перейти к следующему правилу\n"
        else:
            report += "Невозможно построить план: нет подходящих правил\n"

        report += "\n" + "=" * 70

        return report

    def extract_conditions(self, condition_text: str) -> List[str]:
        """Извлечение условий из текста условия"""
        # Простой парсер для демонстрации
        conditions = []

        # Разбиваем по "и", "или"
        parts = re.split(r'\s+и\s+|\s+или\s+', condition_text, flags=re.IGNORECASE)

        for part in parts:
            part = part.strip()
            if part:
                conditions.append(part)

        return conditions

    def new_domain(self):
        """Создание новой предметной области"""
        name, ok = QInputDialog.getText(
            self, "Новая предметная область",
            "Введите название предметной области:"
        )

        if ok and name:
            description, ok_desc = QInputDialog.getText(
                self, "Описание",
                "Введите описание предметной области (необязательно):"
            )

            if ok_desc:
                domain = self.db_manager.create_domain(name, description)

                if domain:
                    QMessageBox.information(self, "Успех",
                                            f"Создана предметная область: {name}")
                    self.current_domain_id = domain['id']
                    self.statusBar().showMessage(f"Создана предметная область: {name}")
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        "Не удалось создать предметную область")

    def new_agent(self):
        """Создание нового агента"""
        name, ok = QInputDialog.getText(
            self, "Новый агент",
            "Введите имя агента:"
        )

        if ok and name:
            # Выбор домена
            domains = self.db_manager.get_all_domains()

            if not domains:
                QMessageBox.warning(self, "Ошибка",
                                    "Сначала создайте предметную область")
                return

            domain_names = [domain['name'] for domain in domains]
            domain_name, ok_domain = QInputDialog.getItem(
                self, "Выбор предметной области",
                "Выберите предметную область для агента:",
                domain_names, 0, False
            )

            if ok_domain:
                # Находим ID домена
                domain_id = None
                for domain in domains:
                    if domain['name'] == domain_name:
                        domain_id = domain['id']
                        break

                description, ok_desc = QInputDialog.getText(
                    self, "Описание",
                    "Введите описание агента (необязательно):"
                )

                if ok_desc:
                    agent = self.db_manager.create_agent(
                        name=name,
                        domain_id=domain_id,
                        description=description
                    )

                    if agent:
                        QMessageBox.information(self, "Успех",
                                                f"Создан агент: {name}")
                        self.current_agent_id = agent['id']
                        self.statusBar().showMessage(f"Создан агент: {name}")
                    else:
                        QMessageBox.warning(self, "Ошибка",
                                            "Не удалось создать агента")

    def show_statistics(self):
        """Показать статистику базы данных"""
        stats = self.db_manager.get_statistics()

        stats_text = "📊 СТАТИСТИКА БАЗЫ ДАННЫХ\n"
        stats_text += "=" * 40 + "\n\n"

        stats_text += f"Предметные области: {stats.get('domains', 0)}\n"
        stats_text += f"Агенты: {stats.get('agents', 0)}\n"
        stats_text += f"Правила: {stats.get('rules', 0)}\n"
        stats_text += f"Факты: {stats.get('facts', 0)}\n\n"

        if 'rules_by_type' in stats:
            stats_text += "Правила по типам:\n"
            for rule_type, count in stats['rules_by_type'].items():
                stats_text += f"  • {rule_type}: {count}\n"

        # Показываем в диалоговом окне
        dialog = QDialog(self)
        dialog.setWindowTitle("Статистика")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setPlainText(stats_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec_()

    def export_data(self):
        """Экспорт данных в JSON"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт базы данных", "",
            "JSON файлы (*.json);;Все файлы (*)"
        )

        if filename:
            if not filename.endswith('.json'):
                filename += '.json'

            success = self.db_manager.export_to_json(filename)

            if success:
                QMessageBox.information(self, "Успех",
                                        f"База данных экспортирована в {filename}")
                self.statusBar().showMessage(f"Экспорт в {filename} выполнен")
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Не удалось экспортировать базу данных")

    def import_data(self):
        """Импорт данных из JSON"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Импорт базы данных", "",
            "JSON файлы (*.json);;Все файлы (*)"
        )

        if filename:
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Импортировать базу данных? Существующие данные не будут удалены.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.db_manager.import_from_json(filename)

                if success:
                    QMessageBox.information(self, "Успех",
                                            f"База данных импортирована из {filename}")

                    # Обновляем данные
                    self.refresh_rules_table()
                    self.refresh_facts_table()

                    self.statusBar().showMessage(f"Импорт из {filename} выполнен")
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        "Не удалось импортировать базу данных")

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        Система анализа текста и управления базами знаний

        Версия: 1.0
        Разработчик: Система поддержки принятия решений

        Функции:
        • Анализ текста и извлечение продукционных правил
        • Управление базами знаний экспертов (агентов)
        • Трассировка и сравнение баз знаний
        • Прямой и обратный вывод
        • Экспорт/импорт данных

        Используемые технологии:
        • Python 3.8+
        • PyQt5 для графического интерфейса
        • SQLite для хранения данных
        """

        QMessageBox.about(self, "О программе", about_text)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()