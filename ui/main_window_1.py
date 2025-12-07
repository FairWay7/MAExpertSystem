from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from datetime import datetime
import uuid

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_kb = None
        self.agents = {}  # Словарь для хранения агентов
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
        
        # Вкладка базы знаний (правила)
        self.kb_rules_widget = QWidget()
        kb_rules_layout = QVBoxLayout(self.kb_rules_widget)
        
        # Панель инструментов для правил
        rules_toolbar = QHBoxLayout()
        self.btn_refresh_rules = QPushButton("Обновить")
        self.btn_edit_rule = QPushButton("Редактировать")
        self.btn_delete_rule = QPushButton("Удалить")
        self.btn_change_priority = QPushButton("Изменить приоритет")
        
        rules_toolbar.addWidget(self.btn_refresh_rules)
        rules_toolbar.addWidget(self.btn_edit_rule)
        rules_toolbar.addWidget(self.btn_delete_rule)
        rules_toolbar.addWidget(self.btn_change_priority)
        rules_toolbar.addStretch()
        
        # Таблица правил
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(8)
        self.rules_table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Условие', 'Действие', 'Агент', 
            'Приоритет', 'Автор', 'Дата'
        ])
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        kb_rules_layout.addLayout(rules_toolbar)
        kb_rules_layout.addWidget(self.rules_table)
        self.tab_widget.addTab(self.kb_rules_widget, "Правила")
        
        # Вкладка фактов
        self.facts_widget = QWidget()
        facts_layout = QVBoxLayout(self.facts_widget)
        
        self.facts_table = QTableWidget()
        self.facts_table.setColumnCount(7)
        self.facts_table.setHorizontalHeaderLabels([
            'ID', 'Переменная', 'Значение', 'Агент', 'Автор', 'Достоверность', 'Дата'
        ])
        
        facts_layout.addWidget(self.facts_table)
        self.tab_widget.addTab(self.facts_widget, "Факты")
        
        # Вкладка трассировки
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.tab_widget.addTab(self.trace_text, "Трассировка")
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.tab_widget, 3)
        
        # Подключение сигналов
        self.btn_load_file.clicked.connect(self.load_file)
        self.btn_analyze.clicked.connect(self.analyze_text)
        self.btn_view_rules.clicked.connect(self.view_rules)
        self.btn_trace_agent.clicked.connect(self.trace_agent)
        self.btn_trace_multi.clicked.connect(self.trace_multiple_agents)
        self.btn_forward.clicked.connect(self.forward_inference)
        self.btn_backward.clicked.connect(self.backward_inference)
        self.btn_refresh_rules.clicked.connect(self.view_rules)
        
        # Меню
        self._create_menu_bar()
        
        # Статус бар
        self.statusBar().showMessage('In work')
        
        # Создаем тестовые данные для демонстрации
        self._create_demo_data()
    
    def _create_menu_bar(self):
        """Создание меню приложения"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        new_domain_action = QAction('Новая предметная область', self)
        new_domain_action.triggered.connect(self.new_domain)
        file_menu.addAction(new_domain_action)
        
        load_file_action = QAction('Загрузить файл', self)
        load_file_action.triggered.connect(self.load_file)
        file_menu.addAction(load_file_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Агенты
        agent_menu = menubar.addMenu('Агенты')
        
        new_agent_action = QAction('Новый агент', self)
        new_agent_action.triggered.connect(self.new_agent)
        agent_menu.addAction(new_agent_action)
        
        manage_agents_action = QAction('Управление агентами', self)
        manage_agents_action.triggered.connect(self.manage_agents)
        agent_menu.addAction(manage_agents_action)
    
    def _create_demo_data(self):
        """Создание демонстрационных данных"""
        # Создаем демо агентов
        self.agents = {
            'expert1': {
                'name': 'Эксперт по медицине',
                'domain': 'Медицина',
                'created': datetime.now()
            },
            'expert2': {
                'name': 'Эксперт по технике',
                'domain': 'Техника',
                'created': datetime.now()
            }
        }
    
    def load_file(self):
        """Загрузка файла"""
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
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def analyze_text(self):
        """Анализ текста и извлечение знаний"""
        text = self.text_edit.toPlainText()
        
        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет текста для анализа")
            return
        
        # В реальном приложении здесь будет вызов TextProcessor
        # Для демонстрации создаем тестовые данные
        
        # Создаем тестовые правила
        test_rules = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Правило температуры',
                'condition': 'температура > 38',
                'action': 'диагноз = "лихорадка"',
                'agent': 'expert1',
                'priority': 1,
                'author': 'Система',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Правило давления',
                'condition': 'давление > 140/90',
                'action': 'диагноз = "гипертония"',
                'agent': 'expert1',
                'priority': 2,
                'author': 'Система',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Правило двигателя',
                'condition': 'температура_двигателя > 100',
                'action': 'статус = "перегрев"',
                'agent': 'expert2',
                'priority': 1,
                'author': 'Система',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        ]
        
        # Создаем тестовые факты
        test_facts = [
            {
                'id': str(uuid.uuid4()),
                'variable': 'температура',
                'value': '39.5',
                'agent': 'expert1',
                'author': 'Система',
                'confidence': 0.95,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'id': str(uuid.uuid4()),
                'variable': 'давление',
                'value': '150/95',
                'agent': 'expert1',
                'author': 'Система',
                'confidence': 0.90,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        ]
        
        # Отображаем результаты
        result_text = "=== РЕЗУЛЬТАТЫ АНАЛИЗА ===\n\n"
        result_text += f"Проанализировано символов: {len(text)}\n"
        result_text += f"Обнаружено возможных правил: {len(test_rules)}\n"
        result_text += f"Обнаружено фактов: {len(test_facts)}\n\n"
        
        result_text += "Извлеченные правила:\n"
        for rule in test_rules:
            result_text += f"• {rule['condition']} → {rule['action']}\n"
        
        result_text += "\nИзвлеченные факты:\n"
        for fact in test_facts:
            result_text += f"• {fact['variable']} = {fact['value']}\n"
        
        self.results_text.setText(result_text)
        
        # Сохраняем данные для отображения
        self.demo_rules = test_rules
        self.demo_facts = test_facts
        
        self.statusBar().showMessage(f'Анализ завершен. Обнаружено {len(test_rules)} правил и {len(test_facts)} фактов')
    
    def view_rules(self):
        """Просмотр всех правил в базе знаний"""
        try:
            if not hasattr(self, 'demo_rules'):
                # Если нет данных, показываем сообщение
                self.rules_table.setRowCount(0)
                self.statusBar().showMessage('Нет данных для отображения')
                return
            
            # Заполняем таблицу правил
            self.rules_table.setRowCount(len(self.demo_rules))
            
            for row, rule in enumerate(self.demo_rules):
                self.rules_table.setItem(row, 0, QTableWidgetItem(rule['id'][:8] + '...'))
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule['name']))
                self.rules_table.setItem(row, 2, QTableWidgetItem(rule['condition']))
                self.rules_table.setItem(row, 3, QTableWidgetItem(rule['action']))
                
                # Отображаем имя агента вместо ID
                agent_name = self.agents.get(rule['agent'], {}).get('name', rule['agent'])
                self.rules_table.setItem(row, 4, QTableWidgetItem(agent_name))
                
                self.rules_table.setItem(row, 5, QTableWidgetItem(str(rule['priority'])))
                self.rules_table.setItem(row, 6, QTableWidgetItem(rule['author']))
                self.rules_table.setItem(row, 7, QTableWidgetItem(rule['date']))
            
            # Настраиваем ширину столбцов
            self.rules_table.resizeColumnsToContents()
            self.tab_widget.setCurrentIndex(2)  # Переключаемся на вкладку правил
            
            self.statusBar().showMessage(f'Отображено {len(self.demo_rules)} правил')
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить правила: {str(e)}")
    
    def trace_agent(self):
        """Трассировка правил одного агента"""
        try:
            # Диалог выбора агента
            agent_ids = list(self.agents.keys())
            if not agent_ids:
                QMessageBox.information(self, "Информация", "Нет доступных агентов")
                return
            
            agent_id, ok = QInputDialog.getItem(
                self, "Выбор агента", "Выберите агента для трассировки:",
                [self.agents[a]['name'] for a in agent_ids], 0, False
            )
            
            if ok and agent_id:
                # Находим ID агента по имени
                selected_agent_id = None
                for a_id, a_data in self.agents.items():
                    if a_data['name'] == agent_id:
                        selected_agent_id = a_id
                        break
                
                if selected_agent_id:
                    # В реальном приложении здесь будет вызов метода трассировки
                    # Для демонстрации создаем тестовый вывод
                    
                    trace_text = f"=== ТРАССИРОВКА АГЕНТА: {agent_id} ===\n\n"
                    trace_text += f"Предметная область: {self.agents[selected_agent_id]['domain']}\n"
                    trace_text += f"Дата создания: {self.agents[selected_agent_id]['created'].strftime('%Y-%m-%d %H:%M')}\n\n"
                    
                    # Ищем правила агента
                    agent_rules = [r for r in self.demo_rules if r['agent'] == selected_agent_id]
                    trace_text += f"Правила агента ({len(agent_rules)}):\n"
                    
                    for rule in agent_rules:
                        trace_text += f"\nПравило: {rule['name']}\n"
                        trace_text += f"  Условие: {rule['condition']}\n"
                        trace_text += f"  Действие: {rule['action']}\n"
                        trace_text += f"  Приоритет: {rule['priority']}\n"
                    
                    # Поиск схожих правил (демо)
                    if len(agent_rules) > 1:
                        trace_text += "\n=== СХОЖИЕ ПРАВИЛА ===\n"
                        trace_text += "Правило 'температура > 38' и 'температура_двигателя > 100' схожи по структуре\n"
                    
                    # Поиск конфликтных правил (демо)
                    trace_text += "\n=== КОНФЛИКТНЫЕ ПРАВИЛА ===\n"
                    trace_text += "Конфликтных правил не обнаружено\n"
                    
                    self.trace_text.setText(trace_text)
                    self.tab_widget.setCurrentIndex(4)  # Переключаемся на вкладку трассировки
                    
                    self.statusBar().showMessage(f'Выполнена трассировка агента: {agent_id}')
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при трассировке: {str(e)}")
    
    def trace_multiple_agents(self):
        """Сравнение правил нескольких агентов"""
        try:
            if len(self.agents) < 2:
                QMessageBox.information(self, "Информация", "Необходимо минимум 2 агента для сравнения")
                return
            
            # Диалог выбора агентов
            agent_names = [self.agents[a]['name'] for a in self.agents]
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Выбор агентов для сравнения")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Выберите агентов для сравнения:"))
            
            self.agent_checkboxes = []
            for agent_name in agent_names:
                cb = QCheckBox(agent_name)
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
                        selected_agents.append(cb.text())
                
                if len(selected_agents) < 2:
                    QMessageBox.warning(self, "Ошибка", "Выберите минимум 2 агента")
                    return
                
                # В реальном приложении здесь будет сравнение правил
                # Для демонстрации создаем тестовый вывод
                
                trace_text = "=== СРАВНЕНИЕ АГЕНТОВ ===\n\n"
                trace_text += f"Выбранные агенты: {', '.join(selected_agents)}\n\n"
                
                for agent_name in selected_agents:
                    # Находим ID агента
                    agent_id = None
                    for a_id, a_data in self.agents.items():
                        if a_data['name'] == agent_name:
                            agent_id = a_id
                            break
                    
                    if agent_id:
                        agent_rules = [r for r in self.demo_rules if r['agent'] == agent_id]
                        trace_text += f"Агент: {agent_name}\n"
                        trace_text += f"  Количество правил: {len(agent_rules)}\n"
                        trace_text += f"  Предметная область: {self.agents[agent_id]['domain']}\n\n"
                
                # Демонстрация сравнения
                trace_text += "=== АНАЛИЗ СХОЖЕСТИ ===\n"
                trace_text += "Общие темы: диагностика по показателям\n\n"
                
                trace_text += "=== КОНФЛИКТЫ ===\n"
                trace_text += "Конфликтов не обнаружено - агенты работают в разных областях\n"
                
                self.trace_text.setText(trace_text)
                self.tab_widget.setCurrentIndex(4)
                
                self.statusBar().showMessage(f'Сравнение {len(selected_agents)} агентов')
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при сравнении: {str(e)}")
    
    def forward_inference(self):
        """Прямой вывод"""
        try:
            # В реальном приложении здесь будет вызов InferenceEngine
            # Для демонстрации создаем тестовый вывод
            
            result_text = "=== ПРЯМОЙ ВЫВОД ===\n\n"
            result_text += "Начальные факты:\n"
            result_text += "  температура = 39.5\n"
            result_text += "  давление = 150/95\n\n"
            
            result_text += "Шаги вывода:\n"
            result_text += "1. Проверяем правило: температура > 38 → диагноз = 'лихорадка'\n"
            result_text += "   Условие выполнено (39.5 > 38)\n"
            result_text += "   Результат: добавляем факт диагноз = 'лихорадка'\n\n"
            
            result_text += "2. Проверяем правило: давление > 140/90 → диагноз = 'гипертония'\n"
            result_text += "   Условие выполнено (150/95 > 140/90)\n"
            result_text += "   Результат: добавляем факт диагноз = 'гипертония'\n\n"
            
            result_text += "Итоговые факты:\n"
            result_text += "  температура = 39.5\n"
            result_text += "  давление = 150/95\n"
            result_text += "  диагноз = 'лихорадка' (из правила 1)\n"
            result_text += "  диагноз = 'гипертония' (из правила 2)\n\n"
            
            result_text += "Примечание: обнаружен конфликт по переменной 'диагноз'\n"
            
            self.trace_text.setText(result_text)
            self.tab_widget.setCurrentIndex(4)
            
            self.statusBar().showMessage('Прямой вывод выполнен')
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при прямом выводе: {str(e)}")
    
    def backward_inference(self):
        """Обратный вывод"""
        try:
            # Диалог ввода цели
            goal, ok = QInputDialog.getText(
                self, "Обратный вывод", "Введите цель для доказательства (например, 'диагноз'):"
            )
            
            if ok and goal:
                # В реальном приложении здесь будет вызов InferenceEngine.backward_chaining
                # Для демонстрации создаем тестовый вывод
                
                result_text = f"=== ОБРАТНЫЙ ВЫВОД: доказать '{goal}' ===\n\n"
                
                result_text += "Шаги доказательства:\n"
                result_text += f"1. Цель: доказать '{goal}'\n"
                result_text += f"2. Ищем правила, выводящие '{goal}':\n"
                result_text += "   - температура > 38 → диагноз = 'лихорадка'\n"
                result_text += "   - давление > 140/90 → диагноз = 'гипертония'\n\n"
                
                result_text += "3. Доказываем первое правило:\n"
                result_text += "   Цель: доказать 'температура > 38'\n"
                result_text += "   Факт: температура = 39.5\n"
                result_text += "   Условие выполнено: 39.5 > 38 ✓\n\n"
                
                result_text += "4. Доказываем второе правило:\n"
                result_text += "   Цель: доказать 'давление > 140/90'\n"
                result_text += "   Факт: давление = 150/95\n"
                result_text += "   Условие выполнено: 150/95 > 140/90 ✓\n\n"
                
                result_text += "5. Результат:\n"
                result_text += f"   Цель '{goal}' может быть доказана двумя способами:\n"
                result_text += "   - диагноз = 'лихорадка' (из правила 1)\n"
                result_text += "   - диагноз = 'гипертония' (из правила 2)\n"
                
                self.trace_text.setText(result_text)
                self.tab_widget.setCurrentIndex(4)
                
                self.statusBar().showMessage(f'Обратный вывод для цели "{goal}" выполнен')
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при обратном выводе: {str(e)}")
    
    def new_domain(self):
        """Создание новой предметной области"""
        name, ok = QInputDialog.getText(
            self, "Новая предметная область", 
            "Введите название предметной области:"
        )
        
        if ok and name:
            self.current_kb = {'name': name, 'rules': [], 'facts': []}
            self.statusBar().showMessage(f'Создана новая предметная область: {name}')
    
    def new_agent(self):
        """Создание нового агента"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Новый агент")
            dialog.setMinimumWidth(400)
            
            layout = QFormLayout(dialog)
            
            name_edit = QLineEdit()
            domain_edit = QLineEdit()
            
            layout.addRow("Имя агента:", name_edit)
            layout.addRow("Предметная область:", domain_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addRow(button_box)
            
            if dialog.exec_() == QDialog.Accepted:
                agent_name = name_edit.text().strip()
                domain = domain_edit.text().strip()
                
                if not agent_name:
                    QMessageBox.warning(self, "Ошибка", "Имя агента не может быть пустым")
                    return
                
                # Создаем ID агента
                agent_id = f"agent_{len(self.agents) + 1}"
                
                self.agents[agent_id] = {
                    'name': agent_name,
                    'domain': domain,
                    'created': datetime.now()
                }
                
                self.statusBar().showMessage(f'Создан новый агент: {agent_name}')
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при создании агента: {str(e)}")
    
    def manage_agents(self):
        """Управление агентами"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Управление агентами")
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Таблица агентов
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['ID', 'Имя', 'Область', 'Создан'])
            table.setRowCount(len(self.agents))
            
            for row, (agent_id, agent_data) in enumerate(self.agents.items()):
                table.setItem(row, 0, QTableWidgetItem(agent_id))
                table.setItem(row, 1, QTableWidgetItem(agent_data['name']))
                table.setItem(row, 2, QTableWidgetItem(agent_data.get('domain', '')))
                table.setItem(row, 3, QTableWidgetItem(
                    agent_data['created'].strftime('%Y-%m-%d %H:%M')
                ))
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # Кнопки управления
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.exec_()
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при управлении агентами: {str(e)}")

class QHLine(QFrame):
    """Горизонтальная линия"""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

def main():
    app = QApplication(sys.argv)
    
    # Установка стиля
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()