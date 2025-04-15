from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QMenu, QMessageBox, QScrollArea
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt
from src.pages.home_page import PDFViewer  # Импортируем главную страницу
from src.pages.all_books_page import AllBooksPage
from core.category_manager import CategoryManager
from src.pages.settings_page import SettingsPage
from src.pages.login import RegistrationApp
from core.database import DatabaseManager  # Импортируем DatabaseManager
from src.pages.wishlist_page import WishlistPage  # Импортируем страницу вишлиста
from src.pages.report_page import ReportPage  # Импортируем страницу отчетов
import os


class MainWindow(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("BookShelf")
        self.setGeometry(300, 150, 1200, 800)
        self.user_id = user_id  # Сохраняем ID пользователя
        self.is_dark_theme = False
        self.current_font = "Arial"  # Текущий шрифт по умолчанию
        self.db_manager = DatabaseManager("data/database.db")  # Инициализируем менеджер базы данных

        # Если user_id не передан, показываем окно входа
        if not self.user_id:
            self.show_login()
            return

        # Инициализация основного окна
        self.init_ui()

    def show_login(self):
        """Показывает окно входа и устанавливает callback"""
        self.login_window = RegistrationApp()
        self.login_window.set_login_callback(self.handle_login_success)
        self.login_window.show()

    def handle_login_success(self, user_id):
        """Обрабатывает успешный вход"""
        self.user_id = user_id
        self.init_ui()
        self.show()

    def init_ui(self):
        # Главный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setGeometry(300, 150, 1200, 800)

        # Основной layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Создаем навигационную шапку
        self.create_navbar()

        # Стек для переключения страниц
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setGeometry(300, 150, 1200, 800)
        self.layout.addWidget(self.stacked_widget)

        # Добавляем страницы
        self.home_page = PDFViewer(self.user_id)  # Передаем ID пользователя
        self.home_page.setGeometry(300, 150, 1200, 800)
        
        self.all_books_page = AllBooksPage(self.show_book_details)
        self.all_books_page.setGeometry(300, 150, 1200, 800)
        
        self.book_details_page = QWidget()
        self.book_details_page.setGeometry(300, 150, 1200, 800)
        
        self.category_page = CategoryManager(self.user_id)  # Создаем страницу категорий
        self.category_page.setGeometry(300, 150, 1200, 800)
        
        self.settings_page = SettingsPage(self.user_id)
        self.settings_page.setGeometry(300, 150, 1200, 800)

        self.wishlist_page = WishlistPage(self.user_id)  # Создаем страницу вишлиста
        self.wishlist_page.setGeometry(300, 150, 1200, 800)

        self.report_page = ReportPage(self.user_id, self.db_manager)
        self.report_page.setGeometry(300, 150, 1200, 800)

        # Подключаем сигналы страницы настроек
        self.settings_page.theme_changed.connect(self.apply_theme)
        self.settings_page.font_changed.connect(self.apply_font)
        self.settings_page.logout_requested.connect(self.handle_logout)

        # Добавляем страницы в стек
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.all_books_page)
        self.stacked_widget.addWidget(self.book_details_page)
        self.stacked_widget.addWidget(self.category_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.wishlist_page)
        self.stacked_widget.addWidget(self.report_page)

        # Устанавливаем начальную страницу
        self.stacked_widget.setCurrentWidget(self.home_page)

        # Настройка страницы с детальной информацией
        self.setup_book_details_page()

        # Устанавливаем фиксированный размер для всех страниц
        self.setFixedSize(1200, 800)

    def create_navbar(self):
        # Контейнер для навигационной шапки
        navbar = QWidget()
        navbar_layout = QHBoxLayout()
        navbar.setLayout(navbar_layout)
        navbar.setStyleSheet("background-color: #007bff; color: white;")
        navbar.setFixedHeight(50)

        # Логотип приложения
        logo_label = QLabel("BookShelf")
        logo_label.setFont(self.get_font(16, bold=True))
        logo_label.setStyleSheet("color: white;")
        navbar_layout.addWidget(logo_label)

        # Бургерное меню
        menu_button = QPushButton("☰ Меню")
        menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        menu_button.clicked.connect(self.show_menu)
        navbar_layout.addWidget(menu_button)

        # Выравнивание элементов
        navbar_layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(navbar)

    def show_menu(self):
        # Создаем ниспадающее меню
        menu = QMenu(self)
        menu.addAction("Главная", lambda: self.stacked_widget.setCurrentWidget(self.home_page))
        menu.addAction("Все книги", lambda: self.stacked_widget.setCurrentWidget(self.all_books_page))
        menu.addAction("Вишлист", lambda: self.stacked_widget.setCurrentWidget(self.wishlist_page))
        menu.addAction("Категории", lambda: self.stacked_widget.setCurrentWidget(self.category_page))
        menu.addAction("Отчеты", lambda: self.stacked_widget.setCurrentWidget(self.report_page))
        menu.addAction("Настройки", lambda: self.stacked_widget.setCurrentWidget(self.settings_page))
        

        # Настройка стиля для пунктов меню
        menu.setStyleSheet("""
            QMenu {
                font-size: 18px;
                background-color: """ + ("#2b2b2b" if self.is_dark_theme else "#ffffff") + """;
                color: """ + ("#ffffff" if self.is_dark_theme else "#000000") + """;
            }
            QMenu::item:selected {
                background-color: """ + ("#404040" if self.is_dark_theme else "#e0e0e0") + """;
            }
        """)

        # Показываем меню при клике на кнопку "Меню"
        action = menu.exec_(self.mapToGlobal(self.sender().pos()))

    def setup_book_details_page(self):
        """
        Настройка страницы с детальной информацией о книге.
        """
        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Создаем контейнер для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Заголовок книги
        self.details_title_label = QLabel("")
        self.details_title_label.setAlignment(Qt.AlignCenter)
        self.details_title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.details_title_label)

        # Контейнер для обложки
        cover_container = QWidget()
        cover_layout = QVBoxLayout(cover_container)
        self.details_cover_label = QLabel()
        self.details_cover_label.setAlignment(Qt.AlignCenter)
        cover_layout.addWidget(self.details_cover_label)
        layout.addWidget(cover_container)

        # Информация о книге
        info_container = QWidget()
        self.details_info_layout = QVBoxLayout(info_container)
        layout.addWidget(info_container)

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 18px;
                border: none;
                padding: 10px;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.all_books_page))
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        # Устанавливаем контент в область прокрутки
        scroll_area.setWidget(content_widget)

        # Создаем основной layout для страницы
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Устанавливаем layout для страницы
        self.book_details_page.setLayout(main_layout)
        self.book_details_page.setFixedSize(1200, 800)

    def show_book_details(self, title, cover_url, full_page_url, read_url, author, genre, rating, tags, year, isbn):
        """
        Отображает детальную информацию о книге.
        """
        # Очищаем предыдущую информацию
        self.details_title_label.clear()
        self.details_cover_label.clear()
        self.clear_layout(self.details_info_layout)

        # Устанавливаем новый заголовок
        self.details_title_label.setText(title)

        # Устанавливаем новую обложку
        if cover_url and os.path.exists(cover_url):
            pixmap = QPixmap(cover_url)
            self.details_cover_label.setPixmap(pixmap.scaled(280, 400, Qt.KeepAspectRatio))

        # Добавляем новую информацию
        self.add_info_row("Автор:", author)
        self.add_info_row("Жанр:", genre)
        self.add_info_row("Рейтинг:", rating)
        
        # Отображаем теги
        if tags:
            self.add_info_row("Теги:", "\n".join(tags))
        
        self.add_info_row("Год издания:", year)
        self.add_info_row("ISBN:", isbn)

        # Создаем контейнер для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)  # Расстояние между кнопками

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.all_books_page))
        buttons_layout.addWidget(back_button)

        # Кнопка "Добавить в вишлист"
        wishlist_button = QPushButton("Добавить в вишлист")
        wishlist_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        wishlist_button.clicked.connect(lambda: self.add_to_wishlist(title, author, isbn, cover_url))
        buttons_layout.addWidget(wishlist_button)

        # Добавляем контейнер с кнопками в основной layout
        self.details_info_layout.addLayout(buttons_layout)

        # Переключаемся на страницу с деталями
        self.stacked_widget.setCurrentWidget(self.book_details_page)

    def add_to_wishlist(self, title, author, isbn, cover_url=None):
        """Добавляет книгу в вишлист пользователя"""
        try:
            self.db_manager.add_to_wishlist(self.user_id, title, author, isbn, cover_url)
            QMessageBox.information(self, "Успех", "Книга добавлена в вишлист!")
            # Обновляем страницу вишлиста
            self.refresh_wishlist()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить книгу в вишлист: {str(e)}")

    def refresh_wishlist(self):
        """Обновляет содержимое страницы вишлиста"""
        if hasattr(self, 'wishlist_page'):
            self.wishlist_page.load_wishlist()

    def add_info_row(self, label_text, value_text):
        """
        Добавляет строку с информацией о книге.
        """
        # Создаем контейнер для строки
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)

        # Метка
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        label.setFixedWidth(150)  # Фиксированная ширина для меток
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_layout.addWidget(label)

        # Значение
        value = QLabel(str(value_text) if value_text is not None else "")
        value.setStyleSheet("font-size: 16px;")
        value.setWordWrap(True)  # Разрешаем перенос текста
        value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_layout.addWidget(value)

        # Добавляем виджет в layout
        self.details_info_layout.addWidget(row_widget)

    def clear_layout(self, layout):
        """
        Очищает layout от всех дочерних элементов.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_image(self, img_url):
        try:
            from PIL import Image
            from io import BytesIO
            import requests

            response = requests.get(img_url)
            response.raise_for_status()

            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.thumbnail((200, 300))  # Уменьшаем размер изображения
            image_data = BytesIO()
            image.save(image_data, format="PNG")

            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())
            return pixmap
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
            return None

    @staticmethod
    def get_font(size, bold=False):
        font = QFont("Arial", size)
        font.setBold(bold)
        return font

    def apply_theme(self, is_dark):
        """Применение темы ко всему приложению"""
        self.is_dark_theme = is_dark
        
        if is_dark:
            # Темная тема
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
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
                /* Стили для блоков с книгами */
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
            # Светлая тема
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
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
                /* Стили для блоков с книгами */
                QWidget[class="book-widget"] {
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 5px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #f8f8f8;
                }
            """)

        # Применяем тему к страницам
        self.settings_page.apply_theme(is_dark)
        self.home_page.apply_theme(is_dark)
        self.all_books_page.apply_theme(is_dark)
        self.category_page.apply_theme(is_dark)

    def apply_font(self, font_name):
        """Применение шрифта ко всему приложению"""
        self.current_font = font_name
        font = QFont(font_name)
        
        # Применяем шрифт ко всем виджетам
        self.setFont(font)
        self.central_widget.setFont(font)
        self.stacked_widget.setFont(font)
        
        # Обновляем шрифт для всех страниц
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            widget.setFont(font)
            
        # Обновляем стили для сохранения размера шрифта
        self.update_styles()

    def update_styles(self):
        """Обновление стилей с учетом текущего шрифта"""
        base_style = f"""
            QWidget {{
                font-family: {self.current_font};
            }}
            QLabel {{
                font-family: {self.current_font};
            }}
            QPushButton {{
                font-family: {self.current_font};
            }}
            QLineEdit {{
                font-family: {self.current_font};
            }}
            QComboBox {{
                font-family: {self.current_font};
            }}
        """
        
        if self.is_dark_theme:
            base_style += """
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
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
                QLineEdit {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
            """
        
        self.setStyleSheet(base_style)

    def handle_logout(self):
        """Обработка выхода из аккаунта"""
        # Создаем новое окно входа
        self.show_login()
        self.close()  # Закрываем текущее окно