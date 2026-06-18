from typing import List, Dict

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *


def load_initial_data_impl(self):
    """Загрузка начальных данных"""
    # Проверяем наличие доменов
    domains = self.db_manager.get_all_domains()

    if not domains:
        default_domain = self.db_manager.create_domain(
            name="Общая предметная область",
            description="Автоматически созданный домен"
        )
        if default_domain:
            self.current_domain_id = default_domain['id']
            print(f"Создан домен: {default_domain['name']} (ID: {default_domain['id']})")

    # Если домены есть, берем первый
    if not self.current_domain_id:
        domains = self.db_manager.get_all_domains()
        if domains:
            self.current_domain_id = domains[0]['id']

    # Проверяем наличие агентов
    agents = self.db_manager.get_all_agents()

    if not agents:
        if self.current_domain_id:
            default_agent = self.db_manager.create_agent(
                name="Системный эксперт",
                domain_id=self.current_domain_id,
                description="Агент по умолчанию"
            )
            if default_agent:
                self.current_agent_id = default_agent['id']
                print(f"Создан агент: {default_agent['name']} (ID: {default_agent['id']})")
    else:
        # Берем первого агента
        self.current_agent_id = agents[0]['id']

        # Убеждаемся, что current_domain_id соответствует агенту
        agent = self.db_manager.get_agent(self.current_agent_id)
        if agent and agent.get('domain_id'):
            self.current_domain_id = agent['domain_id']

    # Загружаем данные в виджет выбора
    self.selection_widget.load_domains()

    # Устанавливаем выбранную область и агента в виджете
    if self.current_domain_id:
        self.selection_widget.set_selected_domain(self.current_domain_id)

    if self.current_agent_id:
        self.selection_widget.set_selected_agent(self.current_agent_id)

    # Принудительно вызываем сигнал смены агента для обновления таблиц
    if self.current_agent_id:
        self.selection_widget.agentChanged.emit(self.current_agent_id)

    # Загружаем правила и факты
    self.refresh_rules_table(self.current_agent_id)
    self.refresh_facts_table(self.current_agent_id)

    # Выводим информацию о текущем состоянии
    domains_count = len(self.db_manager.get_all_domains())
    agents_count = len(self.db_manager.get_all_agents())
    rules_count = len(self.db_manager.get_all_rules())
    facts_count = len(self.db_manager.get_all_facts())

    self.statusBar().showMessage(
        f"Загружено: {domains_count} областей, {agents_count} агентов, "
        f"{rules_count} правил, {facts_count} фактов"
    )


def on_domain_changed_impl(self, domain_id: int):
    """Обработка смены предметной области"""
    self.current_domain_id = domain_id
    domain = self.db_manager.get_domain(domain_id)
    if domain:
        self.statusBar().showMessage(f"Выбрана область: {domain['name']}")
        self.refresh_rules_table()
        self.refresh_facts_table()


def on_agent_changed_impl(self, agent_id: int):
    """Обработка смены агента"""
    self.current_agent_id = agent_id
    agent = self.db_manager.get_agent(agent_id)
    if agent:
        self.current_domain_id = agent.get('domain_id')
        self.statusBar().showMessage(f"Выбран агент: {agent['name']}")
        self.refresh_rules_table(agent_id)
        self.refresh_facts_table(agent_id)


def load_file_impl(self):
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
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")


def save_text_impl(self):
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
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def analyze_text_impl(self):
    """Анализ текста и извлечение знаний"""
    text = self.text_edit.toPlainText()

    if not text:
        QMessageBox.warning(self, "Ошибка", "Нет текста для анализа")
        return

    if not self.current_agent_id:
        QMessageBox.warning(self, "Ошибка", "Сначала выберите агента")
        return

    try:
        agent = self.db_manager.get_agent(self.current_agent_id)
        domain_id = agent.get('domain_id') if agent else None

        # Используем имя загруженного файла или "текстовый ввод" если файл не загружен
        source_file = self.current_file_name if self.current_file_name else "текстовый ввод"

        source_info = {
            'agent_id': self.current_agent_id,
            'domain_id': domain_id,
            'source_file': source_file,
            'author': 'Пользователь'
        }

        structure = self.text_processor.analyze_text_structure(text)
        extracted_data = self.text_processor.extract_from_text(text, source_info)

        saved_rules = []
        for rule_data in extracted_data['rules']:
            rule_data['agent_id'] = self.current_agent_id
            saved_rule = self.db_manager.save_rule(rule_data)
            if saved_rule:
                saved_rules.append(saved_rule)

        saved_facts = []
        for fact_data in extracted_data['facts']:
            fact_data['agent_id'] = self.current_agent_id
            saved_fact = self.db_manager.save_fact(fact_data)
            if saved_fact:
                saved_facts.append(saved_fact)

        report = create_analysis_report_impl(structure, extracted_data, saved_rules, saved_facts)

        self.results_text.setText(report)
        self.tab_widget.setCurrentIndex(1)
        self.refresh_rules_table(self.current_agent_id)
        self.refresh_facts_table(self.current_agent_id)

        self.statusBar().showMessage(
            f'Анализ завершен. Сохранено {len(saved_rules)} правил и {len(saved_facts)} фактов'
        )

    except Exception as e:
        QMessageBox.critical(self, "Ошибка анализа", f"Произошла ошибка при анализе текста:\n{str(e)}")

def load_file_impl(self):
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
                import os
                self.current_file_name = os.path.basename(filename)
                self.statusBar().showMessage(f'Загружен файл: {filename}')
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

def create_analysis_report_impl(structure: Dict, extracted_data: Dict,
                                saved_rules: List, saved_facts: List) -> str:
    """Создание отчета об анализе"""
    report = "=" * 70 + "\n"
    report += "СТАТИСТИКА ТЕКСТА\n"
    report += "=" * 70 + "\n\n"
    report += f"  Символов: {structure['total_chars']}\n"
    report += f"  Слов: {structure['total_words']}\n"
    report += f"  Предложений: {structure['sentences']}\n"
    report += f"  Потенциальных правил: {structure['potential_rules']}\n"
    report += f"  Потенциальных фактов: {structure['potential_facts']}\n\n"

    report += "=" * 70 + "\n"
    report += "РЕЗУЛЬТАТЫ ИЗВЛЕЧЕНИЯ\n"
    report += "=" * 70 + "\n\n"
    report += f"  Найдено правил: {len(extracted_data['rules'])}\n"
    report += f"  Сохранено правил: {len(saved_rules)}\n"
    report += f"  Найдено фактов: {len(extracted_data['facts'])}\n"
    report += f"  Сохранено фактов: {len(saved_facts)}\n\n"

    if saved_rules:
        report += "=" * 70 + "\n"
        report += "СОХРАНЕННЫЕ ПРАВИЛА\n"
        report += "=" * 70 + "\n\n"
        for i, rule in enumerate(saved_rules, 1):
            report += f"{i}. {rule.get('name', 'Без названия')}\n"
            report += f"   ЕСЛИ: {rule['condition']}\n"
            report += f"   ТО: {rule['action']}\n"
            report += f"   Тип: {rule.get('rule_type', 'conditional')}, "
            report += f"Приоритет: {rule.get('priority', 1)}\n\n"

    if saved_facts:
        report += "=" * 70 + "\n"
        report += "СОХРАНЕННЫЕ ФАКТЫ\n"
        report += "=" * 70 + "\n\n"
        for i, fact in enumerate(saved_facts, 1):
            report += f"{i}. {fact['variable_name']} = {fact['value']}\n"
            report += f"   Достоверность: {fact.get('confidence', 1.0):.2f}\n\n"

    return report


def show_rules_impl(self):
    """Показать вкладку с правилами"""
    self.refresh_rules_table()
    self.tab_widget.setCurrentIndex(2)
    self.statusBar().showMessage("Отображены все правила")


def show_facts_impl(self):
    """Показать вкладку с фактами"""
    self.refresh_facts_table()
    self.tab_widget.setCurrentIndex(3)
    self.statusBar().showMessage("Отображены все факты")


def new_domain_impl(self):
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
                QMessageBox.information(self, "Успех", f"Создана предметная область: {name}")
                self.selection_widget.load_domains()
                self.statusBar().showMessage(f"Создана предметная область: {name}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать предметную область")


def new_agent_impl(self):
    """Создание нового агента"""
    name, ok = QInputDialog.getText(
        self, "Новый агент",
        "Введите имя агента:"
    )

    if ok and name:
        domains = self.db_manager.get_all_domains()

        if not domains:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте предметную область")
            return

        domain_names = [domain['name'] for domain in domains]
        domain_name, ok_domain = QInputDialog.getItem(
            self, "Выбор предметной области",
            "Выберите предметную область для агента:",
            domain_names, 0, False
        )

        if ok_domain:
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
                    QMessageBox.information(self, "Успех", f"Создан агент: {name}")
                    self.selection_widget.load_agents()
                    self.statusBar().showMessage(f"Создан агент: {name}")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось создать агента")


def show_about_impl(self):
    """Показать информацию о программе"""
    about_text = """
    <h2>Система анализа текста и управления базами знаний</h2>

    <p><b>Версия:</b> 2.0</p>
    <p><b>Разработчик:</b> Система поддержки принятия решений</p>

    <h3>Функции:</h3>
    <ul>
        <li>Анализ текста и извлечение продукционных правил</li>
        <li>Управление базами знаний экспертов (агентов)</li>
        <li>Трассировка и сравнение баз знаний</li>
        <li>Прямой и обратный вывод с подсистемой объяснения</li>
        <li>Экспорт/импорт данных</li>
        <li>Поиск правил по переменным</li>
    </ul>

    <h3>Используемые технологии:</h3>
    <ul>
        <li>Python 3.8+</li>
        <li>PyQt5 для графического интерфейса</li>
        <li>SQLite для хранения данных</li>
    </ul>

    <p><i>© 2024 Все права защищены</i></p>
    """
    QMessageBox.about(self, "О программе", about_text)


def show_statistics_impl(self):
    """Показать статистику базы данных"""
    stats = self.db_manager.get_statistics()

    stats_text = "СТАТИСТИКА БАЗЫ ДАННЫХ\n"
    stats_text += "=" * 50 + "\n\n"

    stats_text += f"Предметные области: {stats.get('domains', 0)}\n"
    stats_text += f"Агенты: {stats.get('agents', 0)}\n"
    stats_text += f"Правила: {stats.get('rules', 0)}\n"
    stats_text += f"Факты: {stats.get('facts', 0)}\n\n"

    if 'rules_by_type' in stats:
        stats_text += "📊 Правила по типам:\n"
        for rule_type, count in stats['rules_by_type'].items():
            stats_text += f"  • {rule_type}: {count}\n"

    dialog = QDialog(self)
    dialog.setWindowTitle("Статистика")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)
    text_edit = QTextEdit()
    text_edit.setPlainText(stats_text)
    text_edit.setReadOnly(True)
    text_edit.setFont(QFont("Consolas", 10))
    layout.addWidget(text_edit)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok)
    button_box.accepted.connect(dialog.accept)
    layout.addWidget(button_box)

    dialog.exec_()


def close_event_impl(self, event):
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