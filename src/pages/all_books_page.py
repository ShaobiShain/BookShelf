from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QThread
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os


class BookLoader(QObject):
    # Сигналы для передачи данных о книгах и уведомления о завершении загрузки
    book_loaded = pyqtSignal(str, str, str, str, str, str, str, list, str, str)  # Передаем название, обложку, страницу, ссылку, автора, жанр, рейтинг, теги, год и ISBN
    loading_finished = pyqtSignal()  # Сообщаем, что все книги загружены

    def __init__(self):
        super().__init__()
        # Настраиваем адреса для загрузки книг
        self.base_url = "https://flibusta.su"
        self.book_list_url = f"{self.base_url}/book"

    async def fetch_book_list(self, session, url):
        """
        Загружаем список книг с главной страницы сайта.
        """
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                for book_container in soup.select("div.desc"):
                    # Ищем название книги
                    title_tag = book_container.select_one("div.book_name > a")
                    title = title_tag.get_text(strip=True) if title_tag else "Название не найдено"

                    # Ищем обложку книги
                    img_tag = book_container.select_one("div.cover > a > img")
                    img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "Картинка не найдена"
                    if img_url != "Картинка не найдена":
                        img_url = img_url.replace("/b/img/mini/", "/b/img/big/")
                        img_url = f"{self.base_url}{img_url}"

                    # Ищем страницу с полной информацией о книге
                    full_page_tag = book_container.select_one("div.book_name > a")
                    full_page_url = full_page_tag["href"] if full_page_tag and "href" in full_page_tag.attrs else "Страница книги не найдена"
                    if full_page_url != "Страница книги не найдена":
                        full_page_url = f"{self.base_url}{full_page_url}"

                    # Загружаем подробную информацию о книге
                    details = await self.fetch_book_details(session, full_page_url)

                    # Передаем все данные о книге
                    self.book_loaded.emit(
                        title,
                        img_url,
                        full_page_url,
                        details["read_url"],
                        details["author"],
                        details["genre"],
                        details["rating"],
                        details["tags"],
                        details["year"],
                        details["isbn"]
                    )

        except Exception as e:
            print(f"Что-то пошло не так при загрузке списка книг: {e}")

    async def fetch_book_details(self, session, full_page_url):
        """
        Загружаем подробную информацию о каждой книге.
        """
        try:
            async with session.get(full_page_url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Ищем автора книги
                author_tag = soup.select_one("div.row.author > span.row_content > a")
                author = author_tag.get_text(strip=True) if author_tag else "Автор не найден"

                # Ищем жанр книги
                genre_tag = soup.select_one("div.row.genre > span.row_content > a")
                genre = genre_tag.get_text(strip=True) if genre_tag else "Жанр не найден"

                # Ищем рейтинг книги
                rating_tag = soup.select_one("div.row.rating > span.row_content")
                rating = rating_tag.get_text(strip=True) if rating_tag else "Рейтинг не найден"

                # Собираем все теги книги
                tags = [tag.get_text(strip=True) for tag in soup.select("div.row.tags > span.row_content > a")]
                tags = ", ".join(tags) if tags else "Теги не найдены"

                # Ищем год издания
                year_tag = soup.select_one("div.row.year_public > span.row_content")
                year = year_tag.get_text(strip=True) if year_tag else "Год издания не найден"

                # Ищем ISBN книги
                isbn_tag = soup.select_one("div.row.isbn > span.row_content")
                isbn = isbn_tag.get_text(strip=True) if isbn_tag else "ISBN не найден"

                # Ищем ссылку для чтения книги
                read_button_tag = soup.select_one("div.b_buttons_book > div.btn.list > a")
                read_url = read_button_tag["href"] if read_button_tag and "href" in read_button_tag.attrs else "Ссылка не найдена"
                if read_url != "Ссылка не найдена":
                    read_url = f"{self.base_url}{read_url}"

                return {
                    "read_url": read_url,
                    "author": author,
                    "genre": genre,
                    "rating": rating,
                    "tags": tags.split(", "),
                    "year": year,
                    "isbn": isbn
                }

        except Exception as e:
            print(f"Что-то пошло не так при загрузке информации о книге: {e}")
            return {
                "read_url": "Ссылка не найдена",
                "author": "Автор не найден",
                "genre": "Жанр не найден",
                "rating": "Рейтинг не найден",
                "tags": ["Теги не найдены"],
                "year": "Год издания не найден",
                "isbn": "ISBN не найден"
            }

    def load_books(self):
        """
        Запускаем процесс загрузки книг.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        async def main():
            async with aiohttp.ClientSession(headers=headers) as session:
                await self.fetch_book_list(session, self.book_list_url)
            self.loading_finished.emit()  # Сообщаем, что все книги загружены

        asyncio.run(main())


class AllBooksPage(QWidget):
    def __init__(self, show_book_details_callback):
        super().__init__()
        self.show_book_details_callback = show_book_details_callback
        self.is_data_loaded = False
        
        # Следим за тем, куда добавлять следующую книгу в сетке
        self.row = 0
        self.column = 0
        self.columns_per_row = 4  # Сколько книг помещается в одну строку
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Добавляем заголовок страницы
        title = QLabel("Все книги")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Показываем сообщение о загрузке
        self.loading_label = QLabel("Загрузка книг...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 18px; color: gray;")
        layout.addWidget(self.loading_label)

        # Готовим область для прокрутки списка книг
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scroll_layout.setSpacing(60)  # Настраиваем расстояние между книгами
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)  # Настраиваем отступы от краев
        self.scroll_content.setLayout(self.scroll_layout)
        
        # Настраиваем прокрутку
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll_area)
        
        # Прячем список книг, пока они не загружены
        self.scroll_area.hide()

        # Подключаемся к загрузчику книг
        self.book_loader = BookLoader()
        self.book_loader.book_loaded.connect(self.add_book_widget)
        self.book_loader.loading_finished.connect(self.on_loading_finished)

    def load_books(self):
        """Начинаем загрузку книг"""
        if not self.is_data_loaded:
            # Запускаем загрузку в отдельном потоке
            self.thread = QThread()
            self.book_loader.moveToThread(self.thread)
            self.thread.started.connect(self.book_loader.load_books)
            self.thread.start()
            self.is_data_loaded = True

    def add_book_widget(self, title, img_url, full_page_url, read_url, author, genre, rating, tags, year, isbn):
        """Добавляем книгу в список"""
        # Готовим виджет для книги
        book_widget = QWidget()
        book_widget.setFixedSize(230, 380)  # Задаем размер для книги
        book_widget.setProperty("class", "book-widget")
        book_layout = QVBoxLayout(book_widget)
        book_layout.setContentsMargins(8, 8, 8, 8)  # Настраиваем отступы внутри виджета

        # Загружаем и сохраняем обложку книги
        cover_label = QLabel()
        cover_label.setAlignment(Qt.AlignCenter)
        pixmap = self.load_image(img_url)
        local_cover_path = None
        
        if pixmap:
            # Сохраняем обложку на компьютере
            covers_dir = "covers"
            if not os.path.exists(covers_dir):
                os.makedirs(covers_dir)
            
            # Придумываем имя для файла обложки
            file_name = f"{isbn if isbn and isbn != 'ISBN не найден' else title.replace(' ', '_')}.png"
            local_cover_path = os.path.join(covers_dir, file_name)
            
            # Сохраняем картинку
            pixmap.save(local_cover_path)
            
            # Показываем обложку
            cover_label.setPixmap(pixmap.scaled(180, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        book_layout.addWidget(cover_label)

        # Добавляем название книги
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        title_label.setWordWrap(True)
        book_layout.addWidget(title_label)

        # Добавляем автора
        if author and author != "Автор не найден":
            author_label = QLabel(f"Автор: {author}")
            author_label.setAlignment(Qt.AlignCenter)
            author_label.setStyleSheet("font-size: 12px;")
            author_label.setWordWrap(True)
            book_layout.addWidget(author_label)

        # Размещаем виджет в сетке
        self.scroll_layout.addWidget(book_widget, self.row, self.column)
        
        # Обновляем позицию для следующей книги
        self.column += 1
        if self.column >= self.columns_per_row:
            self.column = 0
            self.row += 1

        # Делаем виджет кликабельным
        book_widget.mousePressEvent = lambda e: self.show_book_details_callback(
            title, local_cover_path or "", full_page_url, read_url, author, genre, rating, tags, year, isbn
        )

    def on_loading_finished(self):
        """Вызывается когда загрузка книг завершена"""
        self.loading_label.hide()
        self.scroll_area.show()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

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
                    padding: 10px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #404040;
                }
                QWidget[class="book-widget"] QLabel {
                    color: #ffffff;
                }
                QScrollArea {
                    border: none;
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
                    padding: 10px;
                }
                QWidget[class="book-widget"]:hover {
                    background-color: #f8f8f8;
                }
                QScrollArea {
                    border: none;
                }
            """)

    def showEvent(self, event):
        """Вызывается при показе страницы"""
        if not self.is_data_loaded:
            self.load_books()
        super().showEvent(event)

    def load_image(self, img_url):
        """Загружает изображение по URL"""
        try:
            import requests
            from PyQt5.QtCore import QByteArray
            
            response = requests.get(img_url)
            response.raise_for_status()
            
            image_data = QByteArray(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            
            return pixmap
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
            return None