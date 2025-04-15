from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QScrollArea, QPushButton, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from core.database import DatabaseManager
import os

class WishlistPage(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager("data/database.db")
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Следим за тем, куда добавлять следующую книгу в сетке
        self.row = 0
        self.col = 0
        self.cols_per_row = 4  # Сколько книг помещается в одну строку
        
        self.setup_ui()
        self.load_wishlist()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Добавляем заголовок страницы
        title = QLabel("Мой вишлист")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(title)

        # Готовим область для прокрутки списка книг
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # Настраиваем прокрутку
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll_area)

    def load_wishlist(self):
        # Убираем все книги, которые были показаны раньше
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        self.row = 0
        self.col = 0
        
        # Получаем список книг из вишлиста
        wishlist_books = self.db.get_wishlist(self.user_id)
        
        if not wishlist_books:
            empty_label = QLabel("Ваш вишлист пуст")
            empty_label.setFont(QFont("Arial", 16))
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            return

        for book in wishlist_books:
            # Готовим виджет для каждой книги
            book_widget = QWidget()
            book_widget.setFixedSize(250, 400)
            book_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 10px;
                    padding: 10px;
                }
                QLabel {
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            book_layout = QVBoxLayout(book_widget)

            # Показываем обложку книги
            cover_label = QLabel()
            cover_label.setAlignment(Qt.AlignCenter)
            # Загружаем картинку обложки, если она есть
            if book.get('cover_url'):
                pixmap = self.load_image(book['cover_url'])
                if pixmap:
                    cover_label.setPixmap(pixmap.scaled(180, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            book_layout.addWidget(cover_label)

            # Добавляем название книги
            title_label = QLabel(book['title'])
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setWordWrap(True)
            title_label.setAlignment(Qt.AlignCenter)
            book_layout.addWidget(title_label)

            # Показываем автора книги
            if book['author']:
                author_label = QLabel(f"Автор: {book['author']}")
                author_label.setFont(QFont("Arial", 10))
                author_label.setWordWrap(True)
                author_label.setAlignment(Qt.AlignCenter)
                book_layout.addWidget(author_label)

            # Добавляем ISBN, если он есть
            if book['isbn']:
                isbn_label = QLabel(f"ISBN: {book['isbn']}")
                isbn_label.setFont(QFont("Arial", 10))
                isbn_label.setAlignment(Qt.AlignCenter)
                book_layout.addWidget(isbn_label)

            # Добавляем кнопку для удаления книги
            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda checked, b=book: self.delete_book(b))
            book_layout.addWidget(delete_button)

            # Размещаем книгу в сетке
            self.grid_layout.addWidget(book_widget, self.row, self.col)
            
            # Переходим к следующей позиции
            self.col += 1
            if self.col >= self.cols_per_row:
                self.col = 0
                self.row += 1

    def delete_book(self, book):
        """Убираем книгу из вишлиста"""
        try:
            self.db.remove_from_wishlist(self.user_id, book['title'], book['author'])
            QMessageBox.information(self, "Успех", "Книга удалена из вишлиста")
            self.load_wishlist()  # Обновляем список
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить книгу: {str(e)}")

    def load_image(self, img_url):
        try:
            # Если это ссылка в интернете
            if img_url and (img_url.startswith('http://') or img_url.startswith('https://')):
                from PIL import Image
                from io import BytesIO
                import requests

                response = requests.get(img_url)
                response.raise_for_status()

                image_data = BytesIO(response.content)
                image = Image.open(image_data)
                image.thumbnail((200, 300))  # Уменьшаем размер картинки
                image_data = BytesIO()
                image.save(image_data, format="PNG")

                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                return pixmap
            
            # Если это путь к файлу на компьютере
            if img_url and not os.path.isabs(img_url):
                img_url = os.path.join(self.base_dir, img_url)
            
            if img_url and os.path.exists(img_url):
                pixmap = QPixmap(img_url)
                return pixmap
            
            return None
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
            return None

    def apply_theme(self, is_dark):
        """Меняем оформление страницы в зависимости от темы"""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: none;
                }
                QLabel {
                    color: #ffffff;
                }
                QWidget[class="book-widget"] {
                    background-color: #363636;
                    border: 1px solid #404040;
                    border-radius: 5px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #404040;
                }
                QWidget[class="book-widget"] QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QScrollArea {
                    background-color: #f0f0f0;
                    border: none;
                }
                QLabel {
                    color: #000000;
                }
                QWidget[class="book-widget"] {
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 5px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #f8f8f8;
                }
            """) 