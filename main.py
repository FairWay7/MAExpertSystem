import sys
import os
import warnings

# Подавляем предупреждения
warnings.filterwarnings('ignore')

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Проверка и установка зависимостей"""
    print("Проверка зависимостей...")

    try:
        import PyQt5
        print("PyQt5 установлен")
    except ImportError:
        print("PyQt5 не установлен. Установите: pip install PyQt5")
        return False

    try:
        import nltk
        print("NLTK установлен")

        # Проверяем необходимые ресурсы NLTK
        try:
            nltk.data.find('tokenizers/punkt')
            print("Ресурсы NLTK доступны")
        except LookupError:
            print("Загружаю ресурсы NLTK...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    except ImportError:
        print("NLTK не установлен. Установите: pip install nltk")
        return False

    return True


def main():
    """Главная функция"""

    # Проверяем зависимости
    if not check_dependencies():
        print("\nПожалуйста, установите все зависимости")
        input("Нажмите Enter для выхода...")
        return

    print("\nЗапуск приложения...")

    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Современный стиль

        window = MainWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()