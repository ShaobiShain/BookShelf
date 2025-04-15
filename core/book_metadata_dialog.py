from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QComboBox, QFileDialog, QScrollArea, QWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import shutil
import os

class BookMetadataDialog(QDialog):
    def __init__(self, db_manager, user_id, initial_title="", initial_cover_path=None, book_data=None):
        super().__init__()
        self.db_manager = db_manager
        self.user_id = user_id
        self.custom_cover_path = None
        self.initial_cover_path = initial_cover_path
        self.should_open_book = False  # Флаг для открытия книги
        self.book_data = book_data  # Данные о книге для редактирования
        
        self.setWindowTitle("Информация о книге")
        self.setFixedSize(1200, 860)  # Устанавливаем фиксированный размер

        # Создаем область прокрутки
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Создаем виджет-контейнер для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Обложка книги
        self.cover_label = QLabel()
        if initial_cover_path and os.path.exists(initial_cover_path):
            pixmap = QPixmap(initial_cover_path)
            self.cover_label.setPixmap(pixmap.scaled(280, 400, Qt.KeepAspectRatio))
        self.cover_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.cover_label)
        
        # Кнопка изменения обложки
        change_cover_btn = QPushButton("Изменить обложку")
        change_cover_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px;
                background-color: #007bff;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        change_cover_btn.clicked.connect(self.change_cover)
        layout.addWidget(change_cover_btn)
        
        # Название
        self.title_label = QLabel("Название:")
        self.title_label.setStyleSheet("font-size: 18px;")
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_input = QLineEdit(initial_title)
        self.title_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)
        
        # Автор
        self.author_label = QLabel("Автор:")
        self.author_label.setStyleSheet("font-size: 18px;")
        self.author_label.setAlignment(Qt.AlignLeft)
        self.author_input = QLineEdit()
        self.author_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_input)
        
        # Год издания
        self.year_label = QLabel("Год издания:")
        self.year_label.setStyleSheet("font-size: 18px;")
        self.year_label.setAlignment(Qt.AlignLeft)
        self.year_input = QSpinBox()
        self.year_input.setStyleSheet("""
            QSpinBox {
                font-size: 18px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.year_input.setRange(1000, 2100)
        self.year_input.setValue(2024)
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_input)
        
        # Категория
        self.category_label = QLabel("Категория:")
        self.category_label.setStyleSheet("font-size: 18px;")
        self.category_label.setAlignment(Qt.AlignLeft)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.category_combo.addItem("Без категории")
        self.load_categories()
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_combo)

        # Кнопки действий
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Кнопка "Читать" (показываем только при редактировании существующей книги)
        if book_data:
            read_button = QPushButton("Читать")
            read_button.clicked.connect(self.read_book)
            read_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 10px;
                    background-color: #28a745;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            button_layout.addWidget(read_button)

        # Кнопки OK и Отмена
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px;
                background-color: #007bff;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px;
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Если есть данные книги, заполняем поля
        if book_data:
            self.fill_book_data()

        # Устанавливаем виджет с контентом в область прокрутки
        scroll_area.setWidget(content_widget)

        # Создаем главный layout и добавляем в него область прокрутки
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def load_categories(self):
        """Загрузка категорий пользователя в комбобокс"""
        self.category_combo.clear()
        self.category_combo.addItem("Без категории", None)
        categories = self.db_manager.get_user_categories(self.user_id)
        for category in categories:
            self.category_combo.addItem(category['category_name'], category['category_id'])
        
        # Если есть данные книги, выбираем её категорию
        if self.book_data and 'category_id' in self.book_data:
            index = self.category_combo.findData(self.book_data['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def fill_book_data(self):
        """Заполнение полей данными существующей книги"""
        if self.book_data:
            self.title_input.setText(self.book_data['title'] if 'title' in self.book_data.keys() else '')
            self.author_input.setText(self.book_data['author'] if 'author' in self.book_data.keys() else '')
            if 'publication_year' in self.book_data.keys() and self.book_data['publication_year']:
                self.year_input.setValue(int(self.book_data['publication_year']))

    def read_book(self):
        """Обработчик кнопки 'Читать'"""
        self.should_open_book = True
        self.accept()

    def change_cover(self):
        """Обработчик изменения обложки"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.custom_cover_path = file_path
            pixmap = QPixmap(file_path)
            self.cover_label.setPixmap(pixmap.scaled(300, 450, Qt.KeepAspectRatio))

    def get_data(self):
        """Получить введенные данные"""
        return {
            'title': self.title_input.text(),
            'author': self.author_input.text(),
            'publication_year': self.year_input.value(),
            'category_id': self.category_combo.currentData(),
            'custom_cover_path': self.custom_cover_path,
            'should_open_book': self.should_open_book
        } 