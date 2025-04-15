from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QMessageBox, QComboBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from core.database import DatabaseManager


class SettingsPage(QWidget):
    # Сигналы для общения с главным окном
    theme_changed = pyqtSignal(bool)  # Говорим главному окну, какую тему включить
    font_changed = pyqtSignal(str)  # Сообщаем, какой шрифт выбрал пользователь
    logout_requested = pyqtSignal()  # Просим главное окно выйти из аккаунта

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager("data/database.db")
        self.is_dark_theme = False
        self.setGeometry(300, 150, 1200, 800)
        self.setup_ui()
        self.load_user_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Делаем отступы по краям и между элементами
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Добавляем заголовок страницы
        title = QLabel("Настройки")
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(title)

        # Готовим секцию с настройками профиля
        profile_section = QWidget()
        profile_layout = QVBoxLayout()
        profile_section.setLayout(profile_layout)
        profile_layout.setSpacing(15)

        # Добавляем поле для имени
        name_layout = QHBoxLayout()
        name_label = QLabel("Имя:  ")
        name_label.setStyleSheet("font-size: 18px;")
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet("font-size: 18px; padding: 8px;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        profile_layout.addLayout(name_layout)

        # Добавляем поле для email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setStyleSheet("font-size: 18px;")
        self.email_edit = QLineEdit()
        self.email_edit.setStyleSheet("font-size: 18px; padding: 8px;")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit)
        profile_layout.addLayout(email_layout)

        # Добавляем кнопку для сохранения изменений
        save_button = QPushButton("Сохранить изменения")
        save_button.setStyleSheet("""
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
        save_button.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_button)

        layout.addWidget(profile_section)

        # Готовим секцию с настройками темы
        theme_section = QWidget()
        theme_layout = QVBoxLayout()
        theme_section.setLayout(theme_layout)
        theme_layout.setSpacing(15)

        theme_label = QLabel("Тема оформления")
        theme_label.setStyleSheet("font-size: 18px;")
        theme_layout.addWidget(theme_label)

        self.theme_button = QPushButton("Включить тёмную тему")
        self.theme_button.setStyleSheet("""
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
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)

        layout.addWidget(theme_section)

        # Готовим секцию с настройками шрифта
        font_section = QWidget()
        font_layout = QVBoxLayout()
        font_section.setLayout(font_layout)
        font_layout.setSpacing(15)

        font_label = QLabel("Шрифт")
        font_label.setStyleSheet("font-size: 18px;")
        font_layout.addWidget(font_label)

        self.font_combo = QComboBox()
        self.font_combo.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 8px;
            }
        """)
        # Выбираем популярные шрифты для выпадающего списка
        self.font_combo.addItems([
            "Arial",
            "Times New Roman",
            "Verdana",
            "Tahoma",
            "Calibri",
            "Georgia",
            "Courier New"
        ])
        self.font_combo.currentTextChanged.connect(self.change_font)
        font_layout.addWidget(self.font_combo)

        layout.addWidget(font_section)

        # Добавляем кнопку для выхода из аккаунта
        logout_button = QPushButton("Выйти из аккаунта")
        logout_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px;
                background-color: #dc3545;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        # Добавляем пустое пространство внизу
        layout.addStretch()

    def load_user_data(self):
        """Загружаем информацию о пользователе из базы данных"""
        query = "SELECT user_name, email FROM users WHERE user_id = ?"
        result = self.db.cursor.execute(query, (self.user_id,)).fetchone()
        if result:
            self.name_edit.setText(result[0])
            self.email_edit.setText(result[1])

    def save_profile(self):
        """Сохраняем изменения в профиле пользователя"""
        new_name = self.name_edit.text().strip()
        new_email = self.email_edit.text().strip()

        if not new_name or not new_email:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return

        try:
            query = "UPDATE users SET user_name = ?, email = ? WHERE user_id = ?"
            self.db.cursor.execute(query, (new_name, new_email, self.user_id))
            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Профиль успешно обновлен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить профиль: {str(e)}")

    def toggle_theme(self):
        """Переключаем тему между светлой и темной"""
        self.is_dark_theme = not self.is_dark_theme
        self.theme_button.setText("Включить светлую тему" if self.is_dark_theme else "Включить тёмную тему")
        self.theme_changed.emit(self.is_dark_theme)

    def logout(self):
        """Просим пользователя подтвердить выход из аккаунта"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выйти из аккаунта?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()

    def apply_theme(self, is_dark):
        """Применяем выбранную тему к странице настроек"""
        self.is_dark_theme = is_dark
        self.theme_button.setText("Включить светлую тему" if is_dark else "Включить тёмную тему")
        
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
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
            """)
        else:
            self.setStyleSheet("")  # Возвращаем стандартную тему 

    def change_font(self, font_name):
        """Сообщаем главному окну о смене шрифта"""
        self.font_changed.emit(font_name) 