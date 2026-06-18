"""UI модули для системы анализа текста"""

from ui.main_window import MainWindow
from ui.selection_widget import SelectionWidget
from ui.rules_table_widget import RulesTableWidget
from ui.explanation_subsystem import ExplanationSubsystem
from ui.styles import APP_STYLES

__all__ = [
    'MainWindow',
    'SelectionWidget',
    'RulesTableWidget',
    'ExplanationSubsystem',
    'APP_STYLES'
]