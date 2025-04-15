import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Добавляем корневую директорию проекта в путь Python
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from core.ui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set application icon
    icon_path = os.path.join(base_dir, 'data/images/Logo1.png')
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()  # Start without user_id to show login first
    sys.exit(app.exec_())