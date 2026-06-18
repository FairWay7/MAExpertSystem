APP_STYLES = """
QMainWindow {
    background-color: #f5f5f5;
}

QTabWidget::pane {
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: white;
}

QTabBar::tab {
    background-color: #e0e0e0;
    padding: 8px 15px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #4a90d9;
}

QPushButton {
    background-color: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:pressed {
    background-color: #2c5a8c;
}

QLineEdit, QTextEdit {
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 5px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #4a90d9;
}

QComboBox {
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 5px;
}

QComboBox:hover {
    border-color: #4a90d9;
}

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
    padding: 8px;
    border: 1px solid #ddd;
    font-weight: bold;
}

QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}
"""