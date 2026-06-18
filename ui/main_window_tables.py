"""Методы работы с таблицами правил и фактов"""

from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def filter_rules_impl(self):
    """Фильтрация правил по поисковому запросу и типу"""
    search_text = self.rules_search_edit.text().lower()
    type_filter = self.rules_type_filter.currentText()

    filtered_rules = []
    for rule in self.all_rules:
        if type_filter != "Все типы":
            if rule.get('rule_type', 'conditional') != type_filter:
                continue

        if search_text:
            if (search_text in rule.get('condition', '').lower() or
                search_text in rule.get('action', '').lower() or
                search_text in rule.get('name', '').lower()):
                filtered_rules.append(rule)
        else:
            filtered_rules.append(rule)

    display_rules_in_table_impl(self, filtered_rules)
    self.rules_status_label.setText(
        f"Показано: {len(filtered_rules)} из {len(self.all_rules)} правил"
    )


def display_rules_in_table_impl(self, rules):
    """Отображение правил в таблице"""
    self.rules_table.setRowCount(len(rules))

    for row, rule in enumerate(rules):
        priority = rule.get('priority', 1)
        indicator = "🔴" if priority >= 8 else "🟡" if priority >= 4 else "🟢"
        self.rules_table.setItem(row, 0, QTableWidgetItem(indicator))
        self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('name', '')))
        self.rules_table.setItem(row, 2, QTableWidgetItem(rule['condition']))
        self.rules_table.setItem(row, 3, QTableWidgetItem(rule['action']))
        self.rules_table.setItem(row, 4, QTableWidgetItem(rule.get('rule_type', 'conditional')))

        priority_item = QTableWidgetItem(str(priority))
        if priority >= 8:
            priority_item.setForeground(QColor(220, 53, 69))
        elif priority >= 4:
            priority_item.setForeground(QColor(255, 193, 7))
        else:
            priority_item.setForeground(QColor(40, 167, 69))
        self.rules_table.setItem(row, 5, priority_item)

        agent_id = rule.get('agent_id')
        agent_name = ""
        if agent_id:
            agent = self.db_manager.get_agent(agent_id)
            agent_name = agent['name'] if agent else str(agent_id)
        self.rules_table.setItem(row, 6, QTableWidgetItem(agent_name))

        created_at = rule.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%d.%m.%Y %H:%M')
            except:
                date_str = created_at[:19]
        else:
            date_str = ''
        self.rules_table.setItem(row, 7, QTableWidgetItem(date_str))


def refresh_rules_table_impl(self, agent_id=None):
    """Обновление таблицы правил"""
    try:
        if agent_id is None:
            agent_id = self.current_agent_id

        if agent_id:
            self.all_rules = self.db_manager.get_rules_by_agent(agent_id)
        else:
            self.all_rules = self.db_manager.get_all_rules()

        filter_rules_impl(self)
    except Exception as e:
        print(f"Ошибка обновления таблицы правил: {e}")


def refresh_facts_table_impl(self, agent_id=None):
    """Обновление таблицы фактов"""
    try:
        if agent_id is None:
            agent_id = self.current_agent_id

        if agent_id:
            facts = self.db_manager.get_facts_by_agent(agent_id)
        else:
            facts = self.db_manager.get_all_facts()

        self.facts_table.setRowCount(len(facts))

        for row, fact in enumerate(facts):
            self.facts_table.setItem(row, 0, QTableWidgetItem(fact['id'][:8] + '...'))
            self.facts_table.setItem(row, 1, QTableWidgetItem(fact['variable_name']))
            self.facts_table.setItem(row, 2, QTableWidgetItem(str(fact['value'])))

            confidence = fact.get('confidence', 1.0)
            confidence_item = QTableWidgetItem(f"{confidence:.2f}")
            if confidence >= 0.8:
                confidence_item.setForeground(QColor(40, 167, 69))
            elif confidence >= 0.5:
                confidence_item.setForeground(QColor(255, 193, 7))
            else:
                confidence_item.setForeground(QColor(220, 53, 69))
            self.facts_table.setItem(row, 3, confidence_item)

            agent_id_val = fact.get('agent_id')
            agent_name = ""
            if agent_id_val:
                agent = self.db_manager.get_agent(agent_id_val)
                agent_name = agent['name'] if agent else str(agent_id_val)
            self.facts_table.setItem(row, 4, QTableWidgetItem(agent_name))

            created_at = fact.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d.%m.%Y %H:%M')
                except:
                    date_str = created_at[:19]
            else:
                date_str = ''
            self.facts_table.setItem(row, 5, QTableWidgetItem(date_str))

        self.facts_table.resizeColumnsToContents()
        self.facts_status_label.setText(f"Всего фактов: {len(facts)}")
    except Exception as e:
        print(f"Ошибка обновления таблицы фактов: {e}")


def delete_selected_rule_impl(self):
    """Удаление выбранного правила"""
    selected_rows = self.rules_table.selectionModel().selectedRows()

    if not selected_rows:
        QMessageBox.warning(self, "Ошибка", "Выберите правило для удаления")
        return

    reply = QMessageBox.question(
        self, 'Подтверждение',
        f'Вы уверены, что хотите удалить выбранное правило ({len(selected_rows)})?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        for index in selected_rows:
            row = index.row()
            if row < len(self.all_rules):
                rule_id = self.all_rules[row]['id']
                self.db_manager.delete_rule(rule_id)

        refresh_rules_table_impl(self, self.current_agent_id)
        self.statusBar().showMessage(f"Удалено {len(selected_rows)} правил")


def edit_rule_priority_impl(self):
    """Изменение приоритета правила"""
    selected_rows = self.rules_table.selectionModel().selectedRows()

    if not selected_rows or len(selected_rows) > 1:
        QMessageBox.warning(self, "Ошибка", "Выберите одно правило для изменения приоритета")
        return

    row = selected_rows[0].row()
    if row >= len(self.all_rules):
        return

    rule = self.all_rules[row]

    priority, ok = QInputDialog.getInt(
        self, "Изменение приоритета",
        f"Введите новый приоритет для правила:\n{rule.get('condition', '')[:100]}",
        value=rule.get('priority', 1),
        min=1, max=10, step=1
    )

    if ok:
        success = self.db_manager.update_rule_priority(rule['id'], priority)
        if success:
            refresh_rules_table_impl(self, self.current_agent_id)
            self.statusBar().showMessage(f"Приоритет изменен на {priority}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось изменить приоритет")


def delete_selected_fact_impl(self):
    """Удаление выбранного факта"""
    selected_rows = self.facts_table.selectionModel().selectedRows()

    if not selected_rows:
        QMessageBox.warning(self, "Ошибка", "Выберите факт для удаления")
        return

    reply = QMessageBox.question(
        self, 'Подтверждение',
        f'Вы уверены, что хотите удалить выбранный факт ({len(selected_rows)})?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        try:
            # Получаем факты для текущего агента или все факты
            if self.current_agent_id:
                facts = self.db_manager.get_facts_by_agent(self.current_agent_id)
            else:
                facts = self.db_manager.get_all_facts()

            deleted_count = 0
            for index in selected_rows:
                row = index.row()
                if row < len(facts):
                    fact_id = facts[row]['id']
                    success = self.db_manager.delete_fact(fact_id)
                    if success:
                        deleted_count += 1

            self.refresh_facts_table(self.current_agent_id)

            if deleted_count > 0:
                self.statusBar().showMessage(f"Удалено {deleted_count} фактов")
            else:
                self.statusBar().showMessage("Не удалось удалить факты")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при удалении факта:\n{str(e)}")
            import traceback
            traceback.print_exc()


def edit_selected_fact_impl(self):
    """Редактирование выбранного факта"""
    selected_rows = self.facts_table.selectionModel().selectedRows()

    if not selected_rows or len(selected_rows) > 1:
        QMessageBox.warning(self, "Ошибка", "Выберите один факт для редактирования")
        return

    # Получаем факты для текущего агента или все факты
    if self.current_agent_id:
        facts = self.db_manager.get_facts_by_agent(self.current_agent_id)
    else:
        facts = self.db_manager.get_all_facts()

    row = selected_rows[0].row()
    if row >= len(facts):
        return

    fact = facts[row]

    # Диалог редактирования
    dialog = QDialog(self)
    dialog.setWindowTitle("Редактирование факта")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)

    layout.addWidget(QLabel("Переменная:"))
    var_edit = QLineEdit(fact['variable_name'])
    layout.addWidget(var_edit)

    layout.addWidget(QLabel("Значение:"))
    val_edit = QLineEdit(str(fact['value']))
    layout.addWidget(val_edit)

    layout.addWidget(QLabel("Достоверность (0-1):"))
    conf_edit = QDoubleSpinBox()
    conf_edit.setRange(0, 1)
    conf_edit.setSingleStep(0.05)
    conf_edit.setValue(fact.get('confidence', 1.0))
    layout.addWidget(conf_edit)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        try:
            # Обновляем факт через репозиторий
            success = self.db_manager.update_fact(
                fact['id'],  # ID факта (строка)
                var_edit.text(),
                val_edit.text(),
                conf_edit.value()
            )
            if success:
                self.refresh_facts_table(self.current_agent_id)
                self.statusBar().showMessage("Факт обновлен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить факт")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при обновлении факта:\n{str(e)}")
            import traceback
            traceback.print_exc()


def search_rules_dialog_impl(self):
    """Диалог поиска по правилам"""
    search_text, ok = QInputDialog.getText(
        self, "Поиск правил",
        "Введите текст для поиска в условиях и действиях:"
    )
    if ok and search_text:
        self.rules_search_edit.setText(search_text)
        filter_rules_impl(self)


def search_facts_dialog_impl(self):
    """Диалог поиска по фактам"""
    search_text, ok = QInputDialog.getText(
        self, "Поиск фактов",
        "Введите название переменной:"
    )
    if ok and search_text:
        facts = self.db_manager.get_all_facts()
        found_facts = [f for f in facts if search_text.lower() in f['variable_name'].lower()]

        result_text = f"Результаты поиска по переменной '{search_text}':\n\n"
        for fact in found_facts:
            result_text += f"• {fact['variable_name']} = {fact['value']}"
            result_text += f" (достоверность: {fact.get('confidence', 1.0):.2f})\n"

        if not found_facts:
            result_text += "Ничего не найдено."

        self.results_text.setText(result_text)
        self.tab_widget.setCurrentIndex(1)


def search_by_variable_impl(self):
    """Поиск правил, использующих указанную переменную"""
    variable, ok = QInputDialog.getText(
        self, "Поиск по переменной",
        "Введите имя переменной для поиска в правилах:"
    )

    if ok and variable:
        rules = self.db_manager.get_all_rules()
        found_rules = []

        for rule in rules:
            if (variable.lower() in rule.get('condition', '').lower() or
                variable.lower() in rule.get('action', '').lower()):
                found_rules.append(rule)

        result_text = f"Результаты поиска правил, использующих переменную '{variable}':\n\n"
        result_text += "=" * 70 + "\n\n"

        if found_rules:
            for i, rule in enumerate(found_rules, 1):
                result_text += f"{i}. {rule.get('name', 'Без названия')}\n"
                result_text += f"   ЕСЛИ: {rule['condition']}\n"
                result_text += f"   ТО: {rule['action']}\n"
                result_text += f"   Приоритет: {rule.get('priority', 1)}\n\n"
        else:
            result_text += "Ничего не найдено.\n"

        self.results_text.setText(result_text)
        self.tab_widget.setCurrentIndex(1)
        self.statusBar().showMessage(f"Найдено {len(found_rules)} правил")