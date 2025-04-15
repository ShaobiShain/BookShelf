import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from core.database import DatabaseManager  # Подключаем менеджер базы данных


class RegistrationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager("data/database.db")  # Подключаемся к базе данных
        self.is_authenticated = False  # Отслеживаем, вошел ли пользователь
        self.current_user_id = None  # Храним ID текущего пользователя
        self.on_login_success = None  # Функция, которая выполнится после успешного входа
        self.init_ui()

    def validate_email(self, email):
        """Проверяем, соответствует ли email стандартному формату"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_password(self, password):
        """Проверяем, достаточно ли надежный пароль"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        if not re.search(r'[A-Z]', password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"
        if not re.search(r'[a-z]', password):
            return False, "Пароль должен содержать хотя бы одну строчную букву"
        if not re.search(r'\d', password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Пароль должен содержать хотя бы один специальный символ"
        return True, ""

    def validate_login(self, login):
        """Проверяем, подходит ли логин по формату"""
        if len(login) < 4:
            return False, "Логин должен содержать минимум 4 символа"
        if not re.match(r'^[a-zA-Z0-9_]+$', login):
            return False, "Логин может содержать только буквы, цифры и символ подчеркивания"
        return True, ""

    def validate_name(self, name):
        """Проверяем, правильно ли введено имя"""
        if len(name) < 2:
            return False, "Имя должно содержать минимум 2 символа"
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s-]+$', name):
            return False, "Имя может содержать только буквы, пробелы и дефисы"
        return True, ""

    def set_login_callback(self, callback):
        """Сохраняем функцию, которая выполнится после успешного входа"""
        self.on_login_success = callback

    def init_ui(self):
        # Настраиваем внешний вид окна
        self.setWindowTitle("Регистрация и Вход")
        self.setGeometry(300, 150, 1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-size: 18px;
            }
            QLabel {
                font-size: 18px;
            }
            QLabel.title {
                font-size: 48px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                font-size: 18px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px 20px;
                font-size: 18px;
                border-radius: 5px;
            }
        """)

        # Создаем виджет для переключения между страницами
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setGeometry(300, 150, 1200, 800)

        # Готовим страницы входа и регистрации
        self.login_page = self.create_login_page()
        self.registration_page = self.create_registration_page()

        # Добавляем страницы в виджет переключения
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.registration_page)

        # Настраиваем основной макет окна
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_login_page(self):
        # Готовим страницу для входа
        login_page = QWidget()
        login_page.setGeometry(300, 150, 1200, 800)

        title_label = QLabel("Вход")
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 30px;")

        login_label = QLabel("Логин:")
        password_label = QLabel("Пароль:")

        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.authenticate_user)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        register_button = QPushButton("Регистрация")
        register_button.clicked.connect(self.show_registration_page)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)

        # Добавляем информацию о политике конфиденциальности
        policy_label = QLabel("Нажимая кнопку 'Войти', вы соглашаетесь с")
        policy_label.setStyleSheet("font-size: 12px; color: #666;")
        
        policy_button = QPushButton("политикой конфиденциальности")
        policy_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007bff;
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #0056b3;
            }
        """)
        policy_button.clicked.connect(self.show_privacy_policy)

        policy_layout = QHBoxLayout()
        policy_layout.addWidget(policy_label)
        policy_layout.addWidget(policy_button)
        policy_layout.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(200, 100, 200, 100)
        
        layout.addWidget(title_label)
        layout.addWidget(login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addWidget(register_button)
        button_layout.addWidget(login_button)

        layout.addLayout(button_layout)
        layout.addLayout(policy_layout)

        login_page.setLayout(layout)
        return login_page

    def create_registration_page(self):
        # Готовим страницу для регистрации
        registration_page = QWidget()
        registration_page.setGeometry(300, 150, 1200, 800)

        title_label = QLabel("Регистрация")
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 30px;")

        name_label = QLabel("Имя:")
        email_label = QLabel("Email:")
        login_label = QLabel("Логин:")
        password_label = QLabel("Пароль:")

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.reg_login_input = QLineEdit()
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.register_user)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_login_page)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(200, 100, 200, 100)
        
        layout.addWidget(title_label)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(login_label)
        layout.addWidget(self.reg_login_input)
        layout.addWidget(password_label)
        layout.addWidget(self.reg_password_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addWidget(back_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        registration_page.setLayout(layout)
        return registration_page

    def register_user(self):
        # Обрабатываем регистрацию нового пользователя
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        login = self.reg_login_input.text().strip()
        password = self.reg_password_input.text()

        # Проверяем, заполнены ли все поля
        if not all([name, email, login, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверяем правильность введенного имени
        is_valid_name, name_error = self.validate_name(name)
        if not is_valid_name:
            QMessageBox.warning(self, "Ошибка", name_error)
            return

        # Проверяем правильность email
        if not self.validate_email(email):
            QMessageBox.warning(self, "Ошибка", "Неверный формат email!")
            return

        # Проверяем правильность логина
        is_valid_login, login_error = self.validate_login(login)
        if not is_valid_login:
            QMessageBox.warning(self, "Ошибка", login_error)
            return

        # Проверяем надежность пароля
        is_valid_password, password_error = self.validate_password(password)
        if not is_valid_password:
            QMessageBox.warning(self, "Ошибка", password_error)
            return

        success = self.db_manager.register_user(name, email, login, password)
        if success:
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрировались!")
            self.show_login_page()  # Переходим на страницу входа
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким Email или Логином уже существует!")

    def authenticate_user(self):
        # Обрабатываем вход пользователя
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not all([login, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверяем правильность логина
        is_valid_login, login_error = self.validate_login(login)
        if not is_valid_login:
            QMessageBox.warning(self, "Ошибка", login_error)
            return

        user = self.db_manager.authenticate_user(login, password)
        if user:
            QMessageBox.information(self, "Успех", "Вы успешно вошли в систему!")
            self.is_authenticated = True
            self.current_user_id = user['user_id']  # Запоминаем ID пользователя
            
            # Выполняем функцию после успешного входа, если она задана
            if self.on_login_success:
                self.on_login_success(self.current_user_id)
            self.close()  # Закрываем окно входа
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def show_registration_page(self):
        # Переключаемся на страницу регистрации
        self.stacked_widget.setCurrentIndex(1)

    def show_login_page(self):
        # Переключаемся на страницу входа
        self.stacked_widget.setCurrentIndex(0)

    def show_privacy_policy(self):
        """Показываем пользователю политику конфиденциальности"""
        policy_text = """
        Политика конфиденциальности BookShelf

        1. Сбор информации
        - Мы собираем только необходимую информацию для работы приложения
        - Ваши личные данные (имя, email, логин) хранятся в зашифрованном виде

        2. Использование данных
        - Ваши данные используются только для работы приложения
        - Мы не передаем ваши данные третьим лицам
        - Мы не используем ваши данные для рекламы

        3. Безопасность
        - Мы используем современные методы шифрования
        - Регулярно обновляем системы безопасности
        - Проводим аудит безопасности

        4. Ваши права
        - Вы можете запросить удаление ваших данных
        - Вы можете изменить свои данные в настройках
        - Вы можете отказаться от использования приложения в любой момент
        """
        
        QMessageBox.information(self, "Политика конфиденциальности", policy_text)

    def closeEvent(self, event):
        # Закрываем соединение с базой данных при выходе из приложения
        self.db_manager.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationApp()
    window.show()
    sys.exit(app.exec_())