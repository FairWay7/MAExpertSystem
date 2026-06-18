from PyQt5.QtWidgets import QFrame


class HorizontalLine(QFrame):
    """Горизонтальная линия"""

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)