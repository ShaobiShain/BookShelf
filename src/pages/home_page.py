from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFileDialog, QAction, QMenuBar, QLineEdit, QMessageBox, QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
from core.database import DatabaseManager
from core.pdf_handler import create_folder_for_book, save_first_page_as_cover, save_all_pages
from core.book_metadata_dialog import BookMetadataDialog
import os
import shutil


class PDFViewer(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Bookmate")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("data/images/icon.png"))  # Устанавливаем иконку приложения

        # Подключаемся к базе данных и запоминаем ID пользователя
        self.db = DatabaseManager("data/database.db")
        self.user_id = user_id

        # Готовим главное окно
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Настраиваем основной макет
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Создаем меню
        self.create_menu()

        # Готовим верхнюю панель
        self.top_panel = QWidget()
        self.top_layout = QHBoxLayout()
        self.top_panel.setLayout(self.top_layout)
        self.layout.addWidget(self.top_panel)

        # Добавляем кнопку для открытия PDF
        self.open_pdf_button = QPushButton("Открыть PDF")
        self.open_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 14px;
                padding: 5px 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.open_pdf_button.clicked.connect(self.open_pdf)
        self.top_layout.addWidget(self.open_pdf_button)

        # Добавляем заголовок для списка книг
        self.history_label = QLabel("Ранее открытые книги:")
        self.history_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.history_label)

        # Готовим область для прокрутки списка книг
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scroll_content.setStyleSheet("QLabel { margin-right: 25px; }")
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Загружаем список ранее открытых книг
        self.load_history()

    def create_menu(self):
        menubar = self.menuBar()

    def load_history(self):
        # Получаем список книг пользователя
        books = self.db.get_books(self.user_id)
        for book in books:
            # Преобразуем данные книги в удобный формат
            book_dict = {
                'book_id': book[0],
                'title': book[1],
                'author': book[2],
                'publication_year': book[3],
                'file_path': book[4],
                'cover_path': book[5],
                'category_id': book[6],
                'category_name': book[7]
            }

            # Пробуем загрузить обложку книги
            cover_path = book_dict['cover_path']
            if not cover_path or not os.path.exists(cover_path):
                continue  # Пропускаем книгу, если обложка не найдена

            pixmap = QPixmap(cover_path)
            if pixmap.isNull():
                continue  # Пропускаем книгу, если не удалось загрузить картинку

            # Готовим виджет для книги
            book_widget = QWidget()
            book_widget.setFixedSize(300, 500)
            book_widget.setProperty("class", "book-widget")
            book_layout = QVBoxLayout(book_widget)

            # Показываем обложку книги
            cover_label = QLabel()
            cover_label.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio))
            cover_label.setAlignment(Qt.AlignCenter)
            book_layout.addWidget(cover_label)

            # Добавляем информацию о книге
            title_label = QLabel(f"<b>{book_dict['title']}</b>")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 14px; margin: 5px 0;")
            book_layout.addWidget(title_label)

            if book_dict['author']:
                author_label = QLabel(f"Автор: {book_dict['author']}")
                author_label.setStyleSheet("font-size: 12px;")
                book_layout.addWidget(author_label)

            if book_dict['publication_year']:
                year_label = QLabel(f"Год: {book_dict['publication_year']}")
                year_label.setStyleSheet("font-size: 12px;")
                book_layout.addWidget(year_label)

            if book_dict['category_name']:
                category_label = QLabel(f"Категория: {book_dict['category_name']}")
                category_label.setStyleSheet("font-size: 12px;")
                book_layout.addWidget(category_label)

            # Делаем книгу кликабельной
            book_widget.mousePressEvent = lambda e, path=book_dict['file_path']: self.show_pdf_window(path)

            # Добавляем книгу в список
            self.scroll_layout.addWidget(book_widget)

    def clear_history(self):
        # Убираем все книги из списка
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def open_pdf(self):
        # Показываем диалог выбора файла
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Открыть PDF файл", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if filepath:
            # Открываем выбранный PDF-файл
            import fitz
            doc = fitz.open(filepath)

            # Получаем название книги из метаданных или используем имя файла
            title = doc.metadata.get("title", os.path.splitext(os.path.basename(filepath))[0])

            # Создаем папку для новой книги
            self.db.cursor.execute("SELECT MAX(book_id) FROM books")
            max_id = self.db.cursor.fetchone()[0]
            book_id = (max_id or 0) + 1
            folder_path = create_folder_for_book(book_id)

            # Сохраняем первую страницу как временную обложку
            temp_cover_path = os.path.join(folder_path, "cover.png")
            save_first_page_as_cover(doc, folder_path)

            # Показываем окно для ввода информации о книге
            dialog = BookMetadataDialog(self.db, self.user_id, title, temp_cover_path)
            if dialog.exec_() == QDialog.Accepted:
                # Получаем введенные данные
                metadata = dialog.get_data()
                
                # Если пользователь выбрал свою обложку, копируем её
                cover_path = temp_cover_path
                if metadata['custom_cover_path']:
                    cover_path = os.path.join(folder_path, "cover" + os.path.splitext(metadata['custom_cover_path'])[1])
                    shutil.copy2(metadata['custom_cover_path'], cover_path)

                # Сохраняем все страницы книги
                save_all_pages(doc, folder_path)

                # Сохраняем информацию о книге в базе данных
                if self.db.add_book(
                    metadata['title'],
                    metadata['author'],
                    metadata['publication_year'],
                    filepath,
                    cover_path,
                    metadata['category_id'],
                    self.user_id
                ):
                    # Обновляем список книг и открываем новую книгу
                    self.clear_history()
                    self.load_history()
                    self.show_pdf_window(filepath)
                else:
                    QMessageBox.warning(self, "Предупреждение", "Эта книга уже есть в вашей библиотеке.")
            else:
                # Если пользователь передумал, удаляем временные файлы
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)

    def get_book_data(self, file_path):
        """Получаем информацию о книге из базы данных"""
        self.db.cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, b.file_path, b.cover_path,
                   b.category_id, c.category_name 
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.category_id
            WHERE b.file_path = ? AND b.user_id = ?
        """, (file_path, self.user_id))
        row = self.db.cursor.fetchone()
        if row:
            # Преобразуем данные в словарь для удобства
            return dict(zip([col[0] for col in self.db.cursor.description], row))
        return None

    def show_pdf_window(self, filepath):
        # Получаем информацию о книге
        book_data = self.get_book_data(filepath)
        
        if not book_data:
            QMessageBox.critical(self, "Ошибка", "Книга не найдена в базе данных")
            return
        
        # Показываем окно для редактирования информации о книге
        dialog = BookMetadataDialog(
            self.db,
            self.user_id,
            book_data['title'],
            book_data['cover_path'],
            book_data
        )
        
        if dialog.exec_() == QDialog.Accepted:
            # Получаем обновленные данные
            metadata = dialog.get_data()
            
            # Если пользователь выбрал новую обложку
            if metadata['custom_cover_path']:
                # Получаем путь к папке из пути к обложке
                folder_path = os.path.dirname(book_data['cover_path'])
                new_cover_path = os.path.join(
                    folder_path,
                    "cover" + os.path.splitext(metadata['custom_cover_path'])[1]
                )
                shutil.copy2(metadata['custom_cover_path'], new_cover_path)
                # Обновляем путь к обложке в базе данных
                self.db.cursor.execute(
                    "UPDATE books SET cover_path = ? WHERE book_id = ?",
                    (new_cover_path, book_data['book_id'])
                )

            # Обновляем информацию о книге в базе данных
            self.db.cursor.execute("""
                UPDATE books 
                SET title = ?, author = ?, publication_year = ?, category_id = ?
                WHERE book_id = ?
            """, (
                metadata['title'],
                metadata['author'],
                metadata['publication_year'],
                metadata['category_id'],
                book_data['book_id']
            ))
            self.db.conn.commit()

            # Обновляем список книг
            self.clear_history()
            self.load_history()

            # Открываем PDF только если была нажата кнопка "Читать"
            if metadata['should_open_book']:
                pdf_window = PDFWindow(filepath)
                pdf_window.exec_()

    def apply_theme(self, is_dark):
        """Применение темы к странице"""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
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
                QWidget[class="book-widget"] {
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 5px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #f8f8f8;
                }
            """)


class PDFWindow(QDialog):
    def __init__(self, filepath):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.setFixedSize(1200, 800)  # Устанавливаем фиксированный размер
        self.setGeometry(300, 150, 1200, 800)  # Устанавливаем позицию и размер

        # Создаем область прокрутки
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Создаем виджет для содержимого
        self.content_widget = QWidget()
        self.layout = QVBoxLayout(self.content_widget)

        # Загружаем PDF
        self.load_pdf(filepath)

        # Устанавливаем виджет с контентом в область прокрутки
        self.scroll_area.setWidget(self.content_widget)

        # Создаем главный layout и добавляем в него область прокрутки
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)

    def load_pdf(self, filepath):
        try:
            import fitz
            doc = fitz.open(filepath)

            # Отображение всех страниц
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()

                # Временно сохраняем изображение в памяти
                img_bytes = pix.tobytes()
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes)

                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                self.layout.addWidget(image_label)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")