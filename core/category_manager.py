import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QFont
from core.database import DatabaseManager
from PyQt5.QtCore import Qt


class CategoryManager(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("BookShelf - Добавление категории")
        self.setGeometry(100, 100, 800, 600)

        # Сохраняем ID пользователя
        self.user_id = user_id

        # Инициализация базы данных
        self.db_manager = DatabaseManager("data/database.db")

        # Центральный виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Главный макет
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Заголовок
        title_label = QLabel("Добавление категории", self)
        title_label.setFont(QFont("Arial", 16))
        main_layout.addWidget(title_label)

        # Форма для ввода данных
        form_layout = QVBoxLayout()

        # Поле для названия категории
        name_label = QLabel("Название:", self)
        self.name_edit = QLineEdit(self)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)

        # Поле для описания категории
        description_label = QLabel("Описание:", self)
        self.description_edit = QLineEdit(self)
        form_layout.addWidget(description_label)
        form_layout.addWidget(self.description_edit)

        # Кнопка сохранения
        save_button = QPushButton("Сохранить", self)
        save_button.clicked.connect(self.save_category)
        form_layout.addWidget(save_button)

        # Кнопка удаления
        delete_button = QPushButton("Удалить", self)
        delete_button.clicked.connect(self.delete_category)
        form_layout.addWidget(delete_button)

        main_layout.addLayout(form_layout)

        # Таблица для отображения категорий
        self.category_table = QTableWidget(self)
        self.category_table.setColumnCount(2)
        self.category_table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.category_table)

        # Загрузка данных из базы данных
        self.load_categories()

    def save_category(self):
        """Сохраняет новую категорию"""
        category_name = self.name_edit.text().strip()
        category_description = self.description_edit.text().strip()
        
        if not category_name:
            QMessageBox.warning(self, "Ошибка", "Введите название категории")
            return

        # Добавляем категорию в базу данных
        if self.db_manager.add_category(category_name, self.user_id, category_description):
            QMessageBox.information(self, "Успех", "Категория успешно добавлена")
            self.load_categories()  # Обновляем список категорий
            self.name_edit.clear()  # Очищаем поле ввода
            self.description_edit.clear()  # Очищаем поле описания
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить категорию")

    def load_categories(self):
        """Загружает список категорий пользователя"""
        self.category_table.setRowCount(0)
        categories = self.db_manager.get_user_categories(self.user_id)
        for category in categories:
            row_position = self.category_table.rowCount()
            self.category_table.insertRow(row_position)
            
            name_item = QTableWidgetItem(category['category_name'])
            name_item.setData(Qt.UserRole, category['category_id'])
            self.category_table.setItem(row_position, 0, name_item)
            
            description_item = QTableWidgetItem(category['category_description'] or "")
            self.category_table.setItem(row_position, 1, description_item)

    def delete_category(self):
        """Удаляет выбранную категорию"""
        selected_items = self.category_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию для удаления")
            return

        # Получаем ID категории из первой выбранной строки
        row = selected_items[0].row()
        category_id = self.category_table.item(row, 0).data(Qt.UserRole)

        # Запрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту категорию?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_category(category_id, self.user_id):
                QMessageBox.information(self, "Успех", "Категория успешно удалена")
                self.load_categories()  # Обновляем список категорий
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить категорию")

    def closeEvent(self, event):
        # Закрываем соединение с базой данных при закрытии окна
        self.db_manager.close()
        event.accept()

    def apply_theme(self, is_dark):
        """Применение темы к странице"""
        if is_dark:
            self.centralWidget().setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: none;
                    padding: 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QTableWidget {
                    background-color: #363636;
                    color: #ffffff;
                    gridline-color: #404040;
                }
                QTableWidget::item {
                    background-color: #363636;
                    color: #ffffff;
                }
                QTableWidget::item:selected {
                    background-color: #404040;
                }
                QHeaderView::section {
                    background-color: #404040;
                    color: #ffffff;
                    padding: 5px;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.centralWidget().setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    gridline-color: #dddddd;
                }
                QTableWidget::item {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTableWidget::item:selected {
                    background-color: #e6e6e6;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 5px;
                    border: 1px solid #cccccc;
                }
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CategoryManager(1)  # Для тестирования используем ID пользователя 1
    window.show()
    sys.exit(app.exec_())