"""Методы экспорта и импорта данных"""

from PyQt5.QtWidgets import *

from ui.main_window_tables import refresh_facts_table_impl, refresh_rules_table_impl


def export_data_impl(self):
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
            QMessageBox.information(self, "Успех", f"База данных экспортирована в {filename}")
            self.statusBar().showMessage(f"Экспорт в {filename} выполнен")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать базу данных")


def import_data_impl(self):
    """Импорт данных из JSON"""
    filename, _ = QFileDialog.getOpenFileName(
        self, "Импорт базы данных", "",
        "JSON файлы (*.json);;Все файлы (*)"
    )

    if filename:
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Импортировать базу данных? Существующие данные не будут удалены.\n\n"
            "При импорте создаются только новые записи, дубликаты пропускаются.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.statusBar().showMessage("Выполняется импорт данных...")
            QApplication.processEvents()  # Обновляем интерфейс

            success = self.db_manager.import_from_json(filename)

            if success:
                QMessageBox.information(self, "Успех", f"База данных импортирована из {filename}")
                self.selection_widget.refresh()
                refresh_rules_table_impl(self)
                refresh_facts_table_impl(self)
                self.statusBar().showMessage(f"Импорт из {filename} выполнен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось импортировать базу данных. Проверьте формат файла.")
                self.statusBar().showMessage("Ошибка импорта")


def export_data_csv_impl(self):
    """Экспорт данных в CSV"""
    filename, _ = QFileDialog.getSaveFileName(
        self, "Экспорт базы данных", "",
        "CSV файлы (*.csv);;Все файлы (*)"
    )

    if filename:
        success = self.db_manager.export_to_csv(filename)

        if success:
            QMessageBox.information(self, "Успех", f"База данных экспортирована в {filename}")
            self.statusBar().showMessage(f"Экспорт в {filename} выполнен")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать базу данных")