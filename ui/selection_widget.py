from typing import Optional

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class SelectionWidget(QWidget):
    """Виджет для выбора предметной области и агента"""

    domainChanged = pyqtSignal(str)
    agentChanged = pyqtSignal(str)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.domain_ids = {}
        self.agent_ids = {}
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #888;
            }
            QLabel {
                font-weight: normal;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)

        domain_group = QGroupBox("Предметная область")
        domain_layout = QHBoxLayout(domain_group)

        self.domain_combo = QComboBox()
        self.domain_combo.setMinimumWidth(200)
        self.domain_combo.currentIndexChanged.connect(self.on_domain_changed)

        self.refresh_domains_btn = QPushButton("🔄")
        self.refresh_domains_btn.setFixedSize(30, 30)
        self.refresh_domains_btn.setToolTip("Обновить список областей")
        self.refresh_domains_btn.clicked.connect(self.load_domains)

        self.new_domain_btn = QPushButton("+")
        self.new_domain_btn.setFixedSize(30, 30)
        self.new_domain_btn.setToolTip("Новая предметная область")

        domain_layout.addWidget(self.domain_combo)
        domain_layout.addWidget(self.refresh_domains_btn)
        domain_layout.addWidget(self.new_domain_btn)

        # Группа агента
        agent_group = QGroupBox("Агент (эксперт)")
        agent_layout = QHBoxLayout(agent_group)

        self.agent_combo = QComboBox()
        self.agent_combo.setMinimumWidth(200)
        self.agent_combo.currentIndexChanged.connect(self.on_agent_changed)

        self.refresh_agents_btn = QPushButton("🔄")
        self.refresh_agents_btn.setFixedSize(30, 30)
        self.refresh_agents_btn.setToolTip("Обновить список агентов")
        self.refresh_agents_btn.clicked.connect(self.load_agents)

        self.new_agent_btn = QPushButton("+")
        self.new_agent_btn.setFixedSize(30, 30)
        self.new_agent_btn.setToolTip("Новый агент")

        agent_layout.addWidget(self.agent_combo)
        agent_layout.addWidget(self.refresh_agents_btn)
        agent_layout.addWidget(self.new_agent_btn)

        # Информационная метка
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")

        layout.addWidget(domain_group, 2)
        layout.addWidget(agent_group, 2)
        layout.addStretch()
        layout.addWidget(self.info_label, 1)

        self.load_domains()

    def load_domains(self):
        """Загрузка списка предметных областей"""
        self.domain_combo.blockSignals(True)
        self.domain_combo.clear()
        self.domain_ids = {}

        domains = self.db_manager.get_all_domains()

        if domains:
            for i, domain in enumerate(domains):
                self.domain_combo.addItem(domain['name'])
                self.domain_ids[i] = domain['id']
            self.domain_combo.setCurrentIndex(0)
        else:
            self.domain_combo.addItem("Нет областей")

        self.domain_combo.blockSignals(False)
        self.load_agents()

    def load_agents(self):
        """Загрузка списка агентов для выбранной области"""
        self.agent_combo.blockSignals(True)
        self.agent_combo.clear()
        self.agent_ids = {}

        current_domain_id = self.get_current_domain_id()

        if current_domain_id:
            agents = self.db_manager.get_agents_by_domain(current_domain_id)

            if agents:
                for i, agent in enumerate(agents):
                    self.agent_combo.addItem(agent['name'])
                    self.agent_ids[i] = agent['id']
                self.agent_combo.setCurrentIndex(0)

                # Обновляем информационную метку
                agent_count = len(agents)
                rules_count = len(self.db_manager.get_rules_by_agent(agents[0]['id']))
                facts_count = len(self.db_manager.get_facts_by_agent(agents[0]['id']))
                self.info_label.setText(f"{agent_count} агент(ов) | {rules_count} правил | {facts_count} фактов")
            else:
                self.agent_combo.addItem("Нет агентов")
                self.info_label.setText("Нет агентов в выбранной области")
        else:
            self.agent_combo.addItem("Нет агентов")
            self.info_label.setText("Выберите предметную область")

        self.agent_combo.blockSignals(False)

        # После загрузки агентов, если есть агент, отправляем сигнал
        agent_id = self.get_current_agent_id()
        if agent_id:
            self.agentChanged.emit(agent_id)

    def set_selected_agent(self, agent_id: str) -> bool:
        """Установка выбранного агента по ID"""
        # Ищем индекс агента
        for idx, aid in self.agent_ids.items():
            if aid == agent_id:
                self.agent_combo.setCurrentIndex(idx)
                return True

        # Если агент не найден в текущем списке, пробуем загрузить заново
        self.load_agents()
        for idx, aid in self.agent_ids.items():
            if aid == agent_id:
                self.agent_combo.setCurrentIndex(idx)
                return True

        return False

    def set_selected_domain(self, domain_id: str) -> bool:
        """Установка выбранной области по ID"""
        for idx, did in self.domain_ids.items():
            if did == domain_id:
                self.domain_combo.setCurrentIndex(idx)
                return True
        return False

    def get_current_domain_id(self) -> Optional[str]:
        """Получение ID текущей предметной области"""
        index = self.domain_combo.currentIndex()
        return self.domain_ids.get(index)

    def get_current_agent_id(self) -> Optional[str]:
        """Получение ID текущего агента"""
        index = self.agent_combo.currentIndex()
        return self.agent_ids.get(index)

    def get_current_domain_name(self) -> str:
        """Получение названия текущей предметной области"""
        return self.domain_combo.currentText()

    def get_current_agent_name(self) -> str:
        """Получение названия текущего агента"""
        return self.agent_combo.currentText()

    def on_domain_changed(self):
        """Обработка смены предметной области"""
        domain_id = self.get_current_domain_id()
        if domain_id:
            self.load_agents()
            self.domainChanged.emit(domain_id)

    def on_agent_changed(self):
        """Обработка смены агента"""
        agent_id = self.get_current_agent_id()
        if agent_id:
            self.agentChanged.emit(agent_id)

    def refresh(self):
        """Обновление всех данных"""
        self.load_domains()