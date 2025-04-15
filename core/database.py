import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_name="data/database.db"):
        # Получаем абсолютный путь к базе данных
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, db_name)
        # Создание директорию data, если она не существует
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Для получения результатов в виде словарей
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_users_table()  # Выполнене миграцию, если нужно
        self.migrate_wishlist_table()  # Добавление вызов миграции wishlist
        self.migrate_books_and_categories()  # Добавляем миграцию для books и categories

    def create_tables(self):
        # Создание таблицы пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Создание таблицы категорий
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_name TEXT NOT NULL,
                category_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Создание таблицы книг
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_id INTEGER,
                title TEXT NOT NULL,
                author TEXT,
                publication_year INTEGER,
                file_path TEXT NOT NULL,
                cover_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (category_id) REFERENCES categories (category_id)
            )
        ''')

        # Создание таблицы вишлиста
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT,
                cover_url TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        self.conn.commit()

    def migrate_users_table(self):
        # Проверка, существует ли столбец user_name в таблице users
        self.cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'user_name' not in columns:
            print("Миграция таблицы users: добавление столбца user_name...")
            # Создание временной таблицы с новой структурой
            self.cursor.execute("""
                CREATE TABLE new_users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    login TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)

            # Копируем данные из старой таблицы в новую
            self.cursor.execute("""
                INSERT INTO new_users (user_id, user_name, login, password, email)
                SELECT user_id, '' AS user_name, login, password, email FROM users
            """)

            # Удаляем старую таблицу
            self.cursor.execute("DROP TABLE users")

            # Переименовываем новую таблицу в users
            self.cursor.execute("ALTER TABLE new_users RENAME TO users")

            self.conn.commit()
            print("Миграция завершена.")

    def migrate_wishlist_table(self):
        """Добавляет поле cover_url в таблицу wishlist, если его нет"""
        self.cursor.execute("PRAGMA table_info(wishlist)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'cover_url' not in columns:
            print("Миграция таблицы wishlist: добавление столбца cover_url...")
            # Создаем временную таблицу с новой структурой
            self.cursor.execute("""
                CREATE TABLE new_wishlist (
                    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    author TEXT,
                    isbn TEXT,
                    cover_url TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Копируем данные из старой таблицы в новую
            self.cursor.execute("""
                INSERT INTO new_wishlist (wishlist_id, user_id, title, author, isbn, added_date)
                SELECT wishlist_id, user_id, title, author, isbn, added_date FROM wishlist
            """)

            # Удаляем старую таблицу
            self.cursor.execute("DROP TABLE wishlist")

            # Переименовываем новую таблицу в wishlist
            self.cursor.execute("ALTER TABLE new_wishlist RENAME TO wishlist")

            self.conn.commit()
            print("Миграция таблицы wishlist завершена.")

    def migrate_books_and_categories(self):
        """Добавляет поле created_at в таблицы books и categories, если его нет"""
        # Проверяем наличие поля created_at в таблице books
        self.cursor.execute("PRAGMA table_info(books)")
        books_columns = [column[1] for column in self.cursor.fetchall()]
        if 'created_at' not in books_columns:
            print("Миграция таблицы books: добавление столбца created_at...")
            # Создаем временную таблицу с новой структурой
            self.cursor.execute("""
                CREATE TABLE new_books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_id INTEGER,
                    title TEXT NOT NULL,
                    author TEXT,
                    publication_year INTEGER,
                    file_path TEXT NOT NULL,
                    cover_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (category_id) REFERENCES categories (category_id)
                )
            """)

            # Копируем данные из старой таблицы в новую
            self.cursor.execute("""
                INSERT INTO new_books (
                    book_id, user_id, category_id, title, author,
                    publication_year, file_path, cover_path, created_at
                )
                SELECT 
                    book_id, user_id, category_id, title, author,
                    publication_year, file_path, cover_path, CURRENT_TIMESTAMP
                FROM books
            """)

            # Удаляем старую таблицу
            self.cursor.execute("DROP TABLE books")

            # Переименовываем новую таблицу
            self.cursor.execute("ALTER TABLE new_books RENAME TO books")

        # Проверяем наличие поля created_at в таблице categories
        self.cursor.execute("PRAGMA table_info(categories)")
        categories_columns = [column[1] for column in self.cursor.fetchall()]
        if 'created_at' not in categories_columns:
            print("Миграция таблицы categories: добавление столбца created_at...")
            # Создаем временную таблицу с новой структурой
            self.cursor.execute("""
                CREATE TABLE new_categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category_name TEXT NOT NULL,
                    category_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Копируем данные из старой таблицы в новую
            self.cursor.execute("""
                INSERT INTO new_categories (
                    category_id, user_id, category_name,
                    category_description, created_at
                )
                SELECT 
                    category_id, user_id, category_name,
                    category_description, CURRENT_TIMESTAMP
                FROM categories
            """)

            # Удаление старую таблицу
            self.cursor.execute("DROP TABLE categories")

            # Переименовываем новую таблицу
            self.cursor.execute("ALTER TABLE new_categories RENAME TO categories")

        self.conn.commit()

    def add_book(self, title, author, publication_year, file_path, cover_path, category_id, user_id):
        try:
            # Проверяем, существует ли книга с таким путем у этого пользователя
            self.cursor.execute(
                "SELECT book_id FROM books WHERE file_path = ? AND user_id = ?",
                (file_path, user_id)
            )
            if self.cursor.fetchone():
                print(f"У вас уже есть книга с путем {file_path}.")
                return False

            # Если книги нет, добавляем её
            self.cursor.execute(
                """INSERT INTO books 
                   (title, author, publication_year, file_path, cover_path, category_id, user_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, author, publication_year, file_path, cover_path, category_id, user_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Ошибка при добавлении книги.")
            return False

    def get_books(self, user_id):
        """Получает все книги пользователя"""
        self.cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, b.file_path, b.cover_path,
                   b.category_id, c.category_name
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = ?
            ORDER BY b.book_id DESC
        """, (user_id,))
        return self.cursor.fetchall()

    def get_book(self, book_id):
        """Получает информацию о конкретной книге"""
        self.cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.publication_year, b.file_path, b.cover_path,
                   b.category_id, c.category_name
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.category_id
            WHERE b.book_id = ?
        """, (book_id,))
        return self.cursor.fetchone()

    def register_user(self, name, email, login, password):
        try:
            self.cursor.execute(
                "INSERT INTO users (user_name, email, login, password) VALUES (?, ?, ?, ?)",
                (name, email, login, password)
            )
            self.conn.commit()
            return True  # Успешная регистрация
        except sqlite3.IntegrityError:
            return False  # Пользователь с таким Email или Логином уже существует

    def authenticate_user(self, login, password):
        self.cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
        user = self.cursor.fetchone()
        return user  # Возвращаем объект пользователя вместо булевого значения

    def add_category(self, category_name, user_id, category_description=None):
        """Добавляет новую категорию"""
        try:
            self.cursor.execute(
                "INSERT INTO categories (category_name, user_id, category_description) VALUES (?, ?, ?)",
                (category_name, user_id, category_description)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("Категория с таким названием уже существует.")
            return False

    def get_all_categories(self, user_id=None):
        if user_id:
            self.cursor.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,))
        else:
            self.cursor.execute("SELECT * FROM categories")
        return self.cursor.fetchall()

    def get_user_categories(self, user_id):
        """Получает список категорий пользователя"""
        self.cursor.execute("""
            SELECT category_id, category_name, category_description
            FROM categories 
            WHERE user_id = ?
            ORDER BY category_name
        """, (user_id,))
        return [dict(zip(['category_id', 'category_name', 'category_description'], row)) 
                for row in self.cursor.fetchall()]

    def add_to_wishlist(self, user_id, title, author, isbn, cover_url=None):
        """Добавляет книгу в вишлист пользователя"""
        try:
            # Проверяем, нет ли уже такой книги в вишлисте пользователя
            self.cursor.execute('''
                SELECT * FROM wishlist 
                WHERE user_id = ? AND title = ? AND author = ?
            ''', (user_id, title, author))
            
            if self.cursor.fetchone():
                raise Exception("Эта книга уже есть в вашем вишлисте")

            # Добавляем книгу в вишлист
            self.cursor.execute('''
                INSERT INTO wishlist (user_id, title, author, isbn, cover_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, title, author, isbn, cover_url))
            
            self.conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Ошибка при добавлении в вишлист: {str(e)}")

    def get_wishlist(self, user_id):
        """Получает список книг из вишлиста пользователя"""
        self.cursor.execute('''
            SELECT * FROM wishlist 
            WHERE user_id = ?
            ORDER BY added_date DESC
        ''', (user_id,))
        return [dict(zip([col[0] for col in self.cursor.description], row))
                for row in self.cursor.fetchall()]

    def remove_from_wishlist(self, user_id, title, author):
        """Удаляет книгу из вишлиста пользователя"""
        try:
            self.cursor.execute('''
                DELETE FROM wishlist 
                WHERE user_id = ? AND title = ? AND author = ?
            ''', (user_id, title, author))
            self.conn.commit()
            return True
        except Exception as e:
            raise Exception(f"Ошибка при удалении из вишлиста: {str(e)}")

    def get_books_by_period(self, user_id, start_date, end_date):
        """Получение книг за определенный период"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                b.title,
                b.author,
                b.publication_year,
                c.category_name,
                c.category_description
            FROM books b
            JOIN users u ON b.user_id = u.user_id
            LEFT JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = ? AND b.created_at BETWEEN ? AND ?
        """, (user_id, start_date, end_date))
        return self.cursor.fetchall()

    def get_wishlist_by_period(self, user_id, start_date, end_date):
        """Получение вишлиста за определенный период"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                w.title,
                w.author,
                w.added_date
            FROM wishlist w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.user_id = ? AND w.added_date BETWEEN ? AND ?
        """, (user_id, start_date, end_date))
        return self.cursor.fetchall()

    def get_categories_by_period(self, user_id, start_date, end_date):
        """Получение категорий за определенный период"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                c.category_name,
                c.category_description,
                c.created_at
            FROM categories c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.user_id = ? AND c.created_at BETWEEN ? AND ?
        """, (user_id, start_date, end_date))
        return self.cursor.fetchall()

    def get_books_by_category(self, user_id, category_id):
        """Получение книг по категории"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                b.title,
                b.author,
                b.publication_year,
                c.category_name,
                c.category_description
            FROM books b
            JOIN users u ON b.user_id = u.user_id
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = ? AND b.category_id = ?
        """, (user_id, category_id))
        return self.cursor.fetchall()

    def get_all_user_books(self, user_id):
        """Получение всех книг пользователя"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                b.title,
                b.author,
                b.publication_year,
                c.category_name,
                c.category_description
            FROM books b
            JOIN users u ON b.user_id = u.user_id
            LEFT JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def get_all_user_wishlist(self, user_id):
        """Получение всего вишлиста пользователя"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                w.title,
                w.author,
                w.added_date
            FROM wishlist w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def get_all_user_categories(self, user_id):
        """Получение всех категорий пользователя"""
        self.cursor.execute("""
            SELECT 
                u.user_name,
                c.category_name,
                c.category_description,
                c.created_at
            FROM categories c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def delete_category(self, category_id, user_id):
        """Удаляет категорию по ID"""
        try:
            # Проверка что категория принадлежит пользователю
            self.cursor.execute("SELECT * FROM categories WHERE category_id = ? AND user_id = ?", 
                              (category_id, user_id))
            if not self.cursor.fetchone():
                return False
            
            # Удаление категории
            self.cursor.execute("DELETE FROM categories WHERE category_id = ? AND user_id = ?", 
                              (category_id, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def close(self):
        self.conn.close()