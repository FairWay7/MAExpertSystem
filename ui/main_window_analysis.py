"""Методы анализа и трассировки"""

from typing import List, Dict
from PyQt5.QtWidgets import *

from core.trace_analyzer import TraceAnalyzer


def trace_agent_impl(self):
    """Трассировка агента с использованием полного анализатора"""
    if not self.current_agent_id:
        QMessageBox.warning(self, "Ошибка", "Сначала выберите агента")
        return

    agent = self.db_manager.get_agent(self.current_agent_id)
    if not agent:
        QMessageBox.warning(self, "Ошибка", "Агент не найден")
        return

    try:
        # Создаем анализатор и выполняем трассировку
        analyzer = TraceAnalyzer(self.db_manager)
        report = analyzer.generate_trace_report(self.current_agent_id)

        self.trace_text.setText(report)
        self.tab_widget.setCurrentIndex(4)
        self.statusBar().showMessage(f"Выполнена полная трассировка агента: {agent['name']}")

    except Exception as e:
        QMessageBox.critical(self, "Ошибка трассировки",
                             f"Произошла ошибка при трассировке:\n{str(e)}")
        import traceback
        traceback.print_exc()


def create_trace_report_impl(agent_name: str, agent_rules: List,
                             similar_rules: List, conflicting_rules: List) -> str:
    """Создание отчета трассировки"""
    report = "=" * 80 + "\n"
    report += f"ОТЧЕТ ТРАССИРОВКИ АГЕНТА: {agent_name}\n"
    report += "=" * 80 + "\n\n"

    report += "СТАТИСТИКА:\n"
    report += "-" * 40 + "\n"
    report += f"  Всего правил: {len(agent_rules)}\n"
    report += f"  Схожих пар правил: {len(similar_rules)}\n"
    report += f"  Конфликтных пар: {len(conflicting_rules)}\n\n"

    if similar_rules:
        report += "СХОЖИЕ ПРАВИЛА:\n"
        report += "-" * 40 + "\n"
        for i, pair in enumerate(similar_rules, 1):
            report += f"{i}. Степень схожести: {pair.get('similarity', 0):.2%}\n"
            report += f"   Правило 1: ЕСЛИ {pair['rule1']['condition'][:100]}\n"
            report += f"             ТО {pair['rule1']['action'][:50]}\n"
            report += f"   Правило 2: ЕСЛИ {pair['rule2']['condition'][:100]}\n"
            report += f"             ТО {pair['rule2']['action'][:50]}\n"
            report += f"   Тип схожести: {pair.get('type', 'unknown')}\n\n"

    if conflicting_rules:
        report += "КОНФЛИКТНЫЕ ПРАВИЛА:\n"
        report += "-" * 40 + "\n"
        for i, conflict in enumerate(conflicting_rules, 1):
            report += f"{i}. Тип конфликта: {conflict.get('conflict_type', 'unknown')}\n"
            report += f"   Схожесть условий: {conflict.get('condition_similarity', 0):.2%}\n"
            report += f"   Правило 1: ЕСЛИ {conflict['rule1']['condition'][:100]}\n"
            report += f"             ТО {conflict['rule1']['action'][:50]}\n"
            report += f"   Правило 2: ЕСЛИ {conflict['rule2']['condition'][:100]}\n"
            report += f"             ТО {conflict['rule2']['action'][:50]}\n\n"

    report += "РЕКОМЕНДАЦИИ:\n"
    report += "-" * 40 + "\n"

    if similar_rules:
        report += "• Рассмотрите возможность объединения схожих правил\n"
    if conflicting_rules:
        report += "• Разрешите конфликты путем изменения приоритетов или условий\n"
    if len(agent_rules) < 5:
        report += "• База знаний мала. Добавьте больше правил\n"
    elif len(agent_rules) > 50:
        report += "• База знаний велика. Рассмотрите возможность оптимизации\n"

    report += "\n" + "=" * 80
    return report


def compare_agents_impl(self):
    """Сравнение нескольких агентов"""
    agents = self.db_manager.get_all_agents()

    if len(agents) < 2:
        QMessageBox.information(self, "Информация", "Для сравнения необходимо минимум 2 агента")
        return

    dialog = QDialog(self)
    dialog.setWindowTitle("Выбор агентов для сравнения")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Выберите агентов для сравнения:"))

    agent_checkboxes = []
    for agent in agents:
        cb = QCheckBox(agent['name'])
        cb.agent_id = agent['id']
        agent_checkboxes.append(cb)
        layout.addWidget(cb)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec_() == QDialog.Accepted:
        selected_agents = []
        for cb in agent_checkboxes:
            if cb.isChecked():
                selected_agents.append({'id': cb.agent_id, 'name': cb.text()})

        if len(selected_agents) < 2:
            QMessageBox.warning(self, "Ошибка", "Выберите минимум 2 агента")
            return

        comparison_report = create_comparison_report_impl(self, selected_agents)
        self.trace_text.setText(comparison_report)
        self.tab_widget.setCurrentIndex(4)
        self.statusBar().showMessage(f"Сравнение {len(selected_agents)} агентов")


def create_comparison_report_impl(self, agents: List[Dict]) -> str:
    """Создание отчета сравнения агентов с использованием полного анализа"""
    report = "=" * 80 + "\n"
    report += "СРАВНЕНИЕ АГЕНТОВ (ПОЛНЫЙ АНАЛИЗ)\n"
    report += "=" * 80 + "\n\n"

    analyzer = TraceAnalyzer(self.db_manager)
    agents_data = []

    for agent in agents:
        analysis = analyzer.analyze_agent_knowledge_base(agent['id'])
        agents_data.append(analysis)

    for data in agents_data:
        report += f"Агент: {data['agent_name']}\n"
        report += f"  Правил: {data['total_rules']}\n"
        report += f"  Фактов: {data['total_facts']}\n"

        # Статистика по типам
        stats = data['rule_statistics']
        report += "  Типы правил:\n"
        for rule_type, count in stats['by_type'].items():
            report += f"    • {rule_type}: {count}\n"

        # Приоритеты
        report += f"  Средний приоритет: {stats['avg_priority']}\n"
        report += f"  Распределение приоритетов:\n"
        report += f"    • Низкий: {stats['priority_distribution']['low']}\n"
        report += f"    • Средний: {stats['priority_distribution']['medium']}\n"
        report += f"    • Высокий: {stats['priority_distribution']['high']}\n"

        # Конфликты и проблемы
        report += f"  Конфликтов: {len(data['conflicting_rules'])}\n"
        report += f"  Схожих пар: {len(data['similar_rules'])}\n"
        report += f"  Слабых правил: {len(data['weak_rules'])}\n"
        report += f"  Избыточных правил: {len(data['redundant_rules'])}\n"
        report += "\n"

    report += "СРАВНИТЕЛЬНЫЙ АНАЛИЗ\n"
    report += "-" * 40 + "\n"

    # Сравнение по количеству правил
    max_rules = max(agents_data, key=lambda x: x['total_rules'])
    min_rules = min(agents_data, key=lambda x: x['total_rules'])

    report += f"• Наибольшее количество правил: {max_rules['agent_name']} ({max_rules['total_rules']})\n"
    report += f"• Наименьшее количество правил: {min_rules['agent_name']} ({min_rules['total_rules']})\n"

    diff = max_rules['total_rules'] - min_rules['total_rules']
    if diff > 0:
        report += f"• Разница: {diff} правил\n"

    # Сравнение по качеству
    total_conflicts = sum(len(d['conflicting_rules']) for d in agents_data)
    if total_conflicts > 0:
        report += f"\nОбщее количество конфликтов: {total_conflicts}\n"

        for data in agents_data:
            if data['conflicting_rules']:
                report += f"  • {data['agent_name']}: {len(data['conflicting_rules'])} конфликтов\n"

    # Рекомендации
    report += "\nРЕКОМЕНДАЦИИ:\n"
    report += "-" * 40 + "\n"

    if diff > 10:
        report += "• Значительная разница в количестве правил между агентами. "
        report += "Рассмотрите возможность обмена знаниями.\n"

    if total_conflicts > 0:
        report += "• Обнаружены конфликты в базах знаний агентов. "
        report += "Рекомендуется провести детальный анализ и разрешить конфликты.\n"

    # Добавляем рекомендации из анализа каждого агента
    report += "\nИНДИВИДУАЛЬНЫЕ РЕКОМЕНДАЦИИ:\n"
    for data in agents_data:
        if data['recommendations']:
            report += f"\n{data['agent_name']}:\n"
            for rec in data['recommendations'][:3]:
                report += f"  • {rec}\n"

    report += "\n" + "=" * 80
    return report