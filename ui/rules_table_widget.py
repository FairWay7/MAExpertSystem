# enhanced_tables.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class RulesTableWidget(QWidget):
    """Улучшенный виджет таблицы правил"""

    ruleSelected = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.rules_data = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Панель инструментов
        toolbar = self.create_toolbar()
        layout.addLayout(toolbar)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            '', 'Название', 'Условие', 'Действие', 'Тип',
            'Приоритет', 'Агент', 'Дата'
        ])

        # Настройка внешнего вида
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)

        # Цветовая схема
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)

        # Установка ширины столбцов
        self.table.setColumnWidth(0, 30)  # Индикатор
        self.table.setColumnWidth(1, 150)  # Название
        self.table.setColumnWidth(2, 250)  # Условие
        self.table.setColumnWidth(3, 250)  # Действие
        self.table.setColumnWidth(4, 80)  # Тип
        self.table.setColumnWidth(5, 70)  # Приоритет
        self.table.setColumnWidth(6, 120)  # Агент
        self.table.setColumnWidth(7, 120)  # Дата

        # Делегат для цветового отображения приоритета
        self.table.setItemDelegate(PriorityDelegate())

        layout.addWidget(self.table)

        # Строка статуса
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QHBoxLayout()

        # Кнопки
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setToolTip("Обновить список правил")

        self.delete_btn = QPushButton("🗑Удалить")
        self.delete_btn.setToolTip("Удалить выбранные правила")
        self.delete_btn.setEnabled(False)

        self.edit_priority_btn = QPushButton("Приоритет")
        self.edit_priority_btn.setToolTip("Изменить приоритет правила")

        self.search_btn = QPushButton("Поиск")
        self.search_btn.setToolTip("Поиск по правилам")

        self.export_btn = QPushButton("Экспорт")
        self.export_btn.setToolTip("Экспорт выбранных правил")

        # Поле поиска
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по условию или действию...")
        self.search_edit.setClearButtonEnabled(True)

        # Фильтр по типу
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все типы", "conditional", "factual", "default"])

        # Фильтр по приоритету
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["Все приоритеты", "1-3 (низкий)", "4-7 (средний)", "8-10 (высокий)"])

        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.edit_priority_btn)
        toolbar.addWidget(self.search_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Поиск:"))
        toolbar.addWidget(self.search_edit)
        toolbar.addWidget(QLabel("Тип:"))
        toolbar.addWidget(self.type_filter)
        toolbar.addWidget(QLabel("Приоритет:"))
        toolbar.addWidget(self.priority_filter)

        return toolbar

    def load_rules(self, agent_id: int = None):
        """Загрузка правил в таблицу"""
        if agent_id:
            rules = self.db_manager.get_rules_by_agent(agent_id)
        else:
            rules = self.db_manager.get_all_rules()

        self.rules_data = rules
        self.apply_filters()

    def apply_filters(self):
        """Применение фильтров"""
        filtered_rules = self.rules_data.copy()

        # Поиск
        search_text = self.search_edit.text().lower()
        if search_text:
            filtered_rules = [r for r in filtered_rules
                              if search_text in r.get('condition', '').lower()
                              or search_text in r.get('action', '').lower()
                              or search_text in r.get('name', '').lower()]

        # Фильтр по типу
        type_filter = self.type_filter.currentText()
        if type_filter != "Все типы":
            filtered_rules = [r for r in filtered_rules
                              if r.get('rule_type', 'conditional') == type_filter]

        # Фильтр по приоритету
        priority_filter = self.priority_filter.currentText()
        if priority_filter == "1-3 (низкий)":
            filtered_rules = [r for r in filtered_rules if 1 <= r.get('priority', 1) <= 3]
        elif priority_filter == "4-7 (средний)":
            filtered_rules = [r for r in filtered_rules if 4 <= r.get('priority', 1) <= 7]
        elif priority_filter == "8-10 (высокий)":
            filtered_rules = [r for r in filtered_rules if 8 <= r.get('priority', 1) <= 10]

        self.display_rules(filtered_rules)
        self.status_label.setText(f"📋 Всего: {len(filtered_rules)} правил (из {len(self.rules_data)})")

    def display_rules(self, rules):
        """Отображение правил в таблице"""
        self.table.setRowCount(len(rules))

        for row, rule in enumerate(rules):
            # Индикатор
            priority = rule.get('priority', 1)
            indicator = self.get_priority_indicator(priority)
            self.table.setItem(row, 0, QTableWidgetItem(indicator))

            # Название
            self.table.setItem(row, 1, QTableWidgetItem(rule.get('name', '')))

            # Условие
            self.table.setItem(row, 2, QTableWidgetItem(rule['condition']))

            # Действие
            self.table.setItem(row, 3, QTableWidgetItem(rule['action']))

            # Тип
            rule_type = rule.get('rule_type', 'conditional')
            type_item = QTableWidgetItem(rule_type)
            type_item.setIcon(self.get_type_icon(rule_type))
            self.table.setItem(row, 4, type_item)

            # Приоритет
            priority_item = QTableWidgetItem(str(priority))
            priority_item.setData(Qt.UserRole, priority)
            self.table.setItem(row, 5, priority_item)

            # Агент
            agent_id = rule.get('agent_id')
            agent_name = ""
            if agent_id:
                agent = self.db_manager.get_agent(agent_id)
                agent_name = agent['name'] if agent else agent_id
            self.table.setItem(row, 6, QTableWidgetItem(agent_name))

            # Дата
            created_at = rule.get('created_at', '')
            date_str = self.format_date(created_at)
            self.table.setItem(row, 7, QTableWidgetItem(date_str))

    def get_priority_indicator(self, priority: int) -> str:
        """Получение индикатора приоритета"""
        if priority >= 8:
            return "🔴"  # Высокий
        elif priority >= 4:
            return "🟡"  # Средний
        else:
            return "🟢"  # Низкий

    def get_type_icon(self, rule_type: str) -> QIcon:
        """Получение иконки типа правила"""
        icons = {
            'conditional': self.create_colored_icon('#3498db'),  # Синий
            'factual': self.create_colored_icon('#2ecc71'),  # Зеленый
            'default': self.create_colored_icon('#95a5a6')  # Серый
        }
        return icons.get(rule_type, QIcon())

    def create_colored_icon(self, color: str) -> QIcon:
        """Создание цветного кружка-иконки"""
        pixmap = QPixmap(12, 12)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)
        painter.end()
        return QIcon(pixmap)

    def format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        if not date_str:
            return ''
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        except:
            return date_str[:19]

    def get_selected_rules(self) -> list:
        """Получение выбранных правил"""
        selected_rows = set()
        for index in self.table.selectionModel().selectedRows():
            selected_rows.add(index.row())

        selected_rules = []
        for row in selected_rows:
            if row < len(self.rules_data):
                selected_rules.append(self.rules_data[row])
        return selected_rules


class PriorityDelegate(QStyledItemDelegate):
    """Делегат для цветового отображения приоритета"""

    def paint(self, painter, option, index):
        priority = index.data(Qt.UserRole)
        if priority:
            if priority >= 8:
                option.palette.setColor(QPalette.Text, QColor(220, 53, 69))  # Красный
            elif priority >= 4:
                option.palette.setColor(QPalette.Text, QColor(255, 193, 7))  # Желтый
            else:
                option.palette.setColor(QPalette.Text, QColor(40, 167, 69))  # Зеленый
        super().paint(painter, option, index)