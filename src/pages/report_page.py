from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QDateEdit, QFileDialog, QMessageBox, QScrollArea,
    QTextEdit
)
from PyQt5.QtCore import Qt, QDate
import pandas as pd
from datetime import datetime
import os
import sqlite3

class ReportPage(QWidget):
    def __init__(self, user_id, db_manager):
        super().__init__()
        self.user_id = user_id
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        # Создаем главный контейнер с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Создаем виджет для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        title = QLabel("Формирование отчетов")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Секция отчета по периоду
        period_group = QWidget()
        period_group.setObjectName("periodGroup")
        period_layout = QVBoxLayout(period_group)
        period_layout.setSpacing(15)
        
        period_title = QLabel("Отчет за период")
        period_title.setObjectName("sectionTitle")
        period_layout.addWidget(period_title)

        # Выбор дат
        dates_widget = QWidget()
        dates_widget.setObjectName("datesWidget")
        dates_layout = QHBoxLayout(dates_widget)
        dates_layout.setSpacing(15)
        
        # Начальная дата
        start_date_label = QLabel("С:")
        start_date_label.setObjectName("dateLabel")
        self.start_date = QDateEdit()
        self.start_date.setObjectName("dateEdit")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background-color: transparent;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit::down-arrow {
                image: none;
            }
            QDateEdit QLineEdit {
                background-color: transparent;
            }
        """)
        dates_layout.addWidget(start_date_label)
        dates_layout.addWidget(self.start_date)
        
        # Конечная дата
        end_date_label = QLabel("По:")
        end_date_label.setObjectName("dateLabel")
        self.end_date = QDateEdit()
        self.end_date.setObjectName("dateEdit")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background-color: transparent;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit::down-arrow {
                image: none;
            }
            QDateEdit QLineEdit {
                background-color: transparent;
            }
        """)
        dates_layout.addWidget(end_date_label)
        dates_layout.addWidget(self.end_date)
        
        period_layout.addWidget(dates_widget)
        
        # Кнопка создания отчета по периоду
        create_period_report_btn = QPushButton("Создать отчет за период")
        create_period_report_btn.setObjectName("reportButton")
        create_period_report_btn.setMinimumHeight(50)
        create_period_report_btn.clicked.connect(self.create_period_report)
        period_layout.addWidget(create_period_report_btn)
        
        layout.addWidget(period_group)

        # Секция отчета по категориям
        category_group = QWidget()
        category_group.setObjectName("categoryGroup")
        category_layout = QVBoxLayout(category_group)
        category_layout.setSpacing(15)
        
        category_title = QLabel("Отчет по категориям")
        category_title.setObjectName("sectionTitle")
        category_layout.addWidget(category_title)

        # Выпадающий список категорий
        category_label = QLabel("Выберите категорию:")
        category_label.setObjectName("fieldLabel")
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setObjectName("categoryCombo")
        self.category_combo.setMinimumHeight(40)
        self.load_categories()
        category_layout.addWidget(self.category_combo)
        
        # Кнопка создания отчета по категории
        create_category_report_btn = QPushButton("Создать отчет по категории")
        create_category_report_btn.setObjectName("reportButton")
        create_category_report_btn.setMinimumHeight(50)
        create_category_report_btn.clicked.connect(self.create_category_report)
        category_layout.addWidget(create_category_report_btn)
        
        layout.addWidget(category_group)

        # Кнопка создания общего отчета
        create_full_report_btn = QPushButton("Создать полный отчет")
        create_full_report_btn.setObjectName("fullReportButton")
        create_full_report_btn.setMinimumHeight(60)
        create_full_report_btn.clicked.connect(self.create_full_report)
        layout.addWidget(create_full_report_btn)

        # Секция сортировки
        self.sort_group = QWidget()
        self.sort_group.setObjectName("sortGroup")
        sort_layout = QVBoxLayout(self.sort_group)
        sort_layout.setSpacing(15)
        
        sort_title = QLabel("Сортировка отчета")
        sort_title.setObjectName("sectionTitle")
        sort_layout.addWidget(sort_title)

        # Выпадающий список для выбора типа сортировки
        sort_type_label = QLabel("Сортировать по:")
        sort_type_label.setObjectName("fieldLabel")
        sort_layout.addWidget(sort_type_label)
        
        self.sort_type_combo = QComboBox()
        self.sort_type_combo.setObjectName("sortCombo")
        self.sort_type_combo.addItem("Дате добавления", "date")
        self.sort_type_combo.addItem("Названию", "name")
        self.sort_type_combo.addItem("Автору", "author")
        sort_layout.addWidget(self.sort_type_combo)

        # Кнопка применения сортировки
        apply_sort_btn = QPushButton("Применить сортировку")
        apply_sort_btn.setObjectName("sortButton")
        apply_sort_btn.clicked.connect(self.apply_sorting)
        sort_layout.addWidget(apply_sort_btn)
        
        layout.addWidget(self.sort_group)

        # Добавляем текстовую область для отображения отчета
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(300)
        self.report_text.setObjectName("reportText")
        layout.addWidget(self.report_text)

        # Устанавливаем виджет с контентом в область прокрутки
        scroll_area.setWidget(content_widget)

        # Создаем главный layout и добавляем в него область прокрутки
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Применяем начальную тему
        self.apply_theme(False)

    def load_categories(self):
        """Загрузка категорий в выпадающий список"""
        self.category_combo.clear()
        categories = self.db_manager.get_user_categories(self.user_id)
        for category in categories:
            self.category_combo.addItem(category['category_name'], category['category_id'])

    def create_period_report(self):
        """Создание отчета за выбранный период"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            # Получаем данные из базы
            books_data = self.db_manager.get_books_by_period(self.user_id, start_date, end_date)
            wishlist_data = self.db_manager.get_wishlist_by_period(self.user_id, start_date, end_date)
            categories_data = self.db_manager.get_categories_by_period(self.user_id, start_date, end_date)
            
            # Применяем выбранную сортировку
            sort_type = self.sort_type_combo.currentData()
            books_data, wishlist_data, categories_data = self.apply_sort_to_data(
                books_data, wishlist_data, categories_data, sort_type
            )
            
            # Создаем отчет
            self.generate_report(books_data, wishlist_data, categories_data, f"report_period_{start_date}_{end_date}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать отчет: {str(e)}")

    def create_category_report(self):
        """Создание отчета по выбранной категории"""
        try:
            category_id = self.category_combo.currentData()
            category_name = self.category_combo.currentText()
            
            # Получаем данные из базы
            books_data = self.db_manager.get_books_by_category(self.user_id, category_id)
            
            # Применяем выбранную сортировку
            sort_type = self.sort_type_combo.currentData()
            books_data, _, _ = self.apply_sort_to_data(books_data, None, None, sort_type)
            
            # Создаем отчет
            self.generate_report(books_data, None, None, f"report_category_{category_name}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать отчет: {str(e)}")

    def create_full_report(self):
        """Создание полного отчета"""
        try:
            # Получаем все данные из базы
            books_data = self.db_manager.get_all_user_books(self.user_id)
            wishlist_data = self.db_manager.get_all_user_wishlist(self.user_id)
            categories_data = self.db_manager.get_all_user_categories(self.user_id)
            
            # Применяем выбранную сортировку
            sort_type = self.sort_type_combo.currentData()
            books_data, wishlist_data, categories_data = self.apply_sort_to_data(
                books_data, wishlist_data, categories_data, sort_type
            )
            
            # Создаем отчет с отсортированными данными
            self.generate_report(books_data, wishlist_data, categories_data, f"full_report_sorted_{sort_type}")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать отчет: {str(e)}")

    def apply_sort_to_data(self, books_data, wishlist_data, categories_data, sort_type):
        """Применяет сортировку к данным в зависимости от выбранного типа"""
        if sort_type == "date":
            # Сортировка по дате добавления
            if books_data:
                books_data = sorted(books_data, key=lambda x: x[3] if x[3] else "", reverse=True)
            if wishlist_data:
                wishlist_data = sorted(wishlist_data, key=lambda x: x[3] if x[3] else "", reverse=True)
            if categories_data:
                categories_data = sorted(categories_data, key=lambda x: x[3] if x[3] else "", reverse=True)
        elif sort_type == "name":
            # Сортировка по названию
            if books_data:
                books_data = sorted(books_data, key=lambda x: x[1].lower() if x[1] else "")
            if wishlist_data:
                wishlist_data = sorted(wishlist_data, key=lambda x: x[1].lower() if x[1] else "")
            if categories_data:
                categories_data = sorted(categories_data, key=lambda x: x[1].lower() if x[1] else "")
        elif sort_type == "author":
            # Сортировка по автору
            if books_data:
                books_data = sorted(books_data, key=lambda x: x[2].lower() if x[2] else "")
            if wishlist_data:
                wishlist_data = sorted(wishlist_data, key=lambda x: x[2].lower() if x[2] else "")
            
        return books_data, wishlist_data, categories_data

    def apply_sorting(self):
        """Метод оставлен для обратной совместимости, но теперь не используется"""
        QMessageBox.information(self, "Информация", "Выберите тип сортировки и нажмите 'Создать полный отчет'")

    def generate_report(self, books_data, wishlist_data, categories_data, filename):
        """Генерация отчета в Excel и отображение на странице"""
        try:
            # Создаем Excel writer
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить отчет", 
                f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel files (*.xlsx)"
            )
            
            if not file_path:
                return

            # Подготавливаем текст для отображения
            report_text = "=== ОТЧЕТ ===\n\n"

            # Добавляем информацию о книгах
            if books_data:
                report_text += "=== КНИГИ ===\n"
                for book in books_data:
                    report_text += f"Название: {book[1]}\n"
                    report_text += f"Автор: {book[2]}\n"
                    report_text += f"Год публикации: {book[3]}\n"
                    report_text += f"Категория: {book[4]}\n"
                    report_text += f"Описание категории: {book[5]}\n"
                    report_text += "-------------------\n"

            # Добавляем информацию о вишлисте
            if wishlist_data:
                report_text += "\n=== ВИШЛИСТ ===\n"
                for item in wishlist_data:
                    report_text += f"Название: {item[1]}\n"
                    report_text += f"Автор: {item[2]}\n"
                    report_text += f"Дата добавления: {item[3]}\n"
                    report_text += "-------------------\n"

            # Добавляем информацию о категориях
            if categories_data:
                report_text += "\n=== КАТЕГОРИИ ===\n"
                for category in categories_data:
                    report_text += f"Название: {category[1]}\n"
                    report_text += f"Описание: {category[2]}\n"
                    report_text += f"Дата создания: {category[3]}\n"
                    report_text += "-------------------\n"

            # Отображаем отчет в текстовой области
            self.report_text.setPlainText(report_text)

            # Сохраняем в Excel
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })

                if books_data:
                    df_books = pd.DataFrame(books_data)
                    df_books.columns = [
                        'Имя пользователя',
                        'Название книги',
                        'Автор',
                        'Год публикации',
                        'Категория',
                        'Описание категории'
                    ]
                    df_books.to_excel(writer, sheet_name='Книги', index=False)
                    worksheet = writer.sheets['Книги']
                    for col_num, value in enumerate(df_books.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 20)

                if wishlist_data:
                    df_wishlist = pd.DataFrame(wishlist_data)
                    df_wishlist.columns = [
                        'Имя пользователя',
                        'Название книги',
                        'Автор',
                        'Дата добавления'
                    ]
                    df_wishlist.to_excel(writer, sheet_name='Вишлист', index=False)
                    worksheet = writer.sheets['Вишлист']
                    for col_num, value in enumerate(df_wishlist.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 20)

                if categories_data:
                    df_categories = pd.DataFrame(categories_data)
                    df_categories.columns = [
                        'Имя пользователя',
                        'Название категории',
                        'Описание категории',
                        'Дата создания'
                    ]
                    df_categories.to_excel(writer, sheet_name='Категории', index=False)
                    worksheet = writer.sheets['Категории']
                    for col_num, value in enumerate(df_categories.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 20)

            QMessageBox.information(self, "Успех", "Отчет успешно создан!")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сгенерировать отчет: {str(e)}")

    def apply_theme(self, is_dark):
        """Применение темы к странице отчетов"""
        if is_dark:
            base_style = """
                QWidget {
                    background-color: #2b2b2b;
                }
                QLabel {
                    color: #ffffff;
                }
                QLabel#pageTitle {
                    font-size: 32px;
                    font-weight: bold;
                    color: #ffffff;
                    padding: 10px;
                    background: transparent;
                }
                QLabel#sectionTitle {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ffffff;
                    padding: 5px;
                    background: transparent;
                }
                QLabel#fieldLabel, QLabel#dateLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #ffffff;
                    padding: 5px;
                    background: transparent;
                }
                QPushButton#reportButton, QPushButton#fullReportButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    min-width: 200px;
                }
                QPushButton#reportButton:hover, QPushButton#fullReportButton:hover {
                    background-color: #1976D2;
                }
                QPushButton#reportButton:pressed, QPushButton#fullReportButton:pressed {
                    background-color: #1565C0;
                }
                QPushButton#fullReportButton {
                    font-size: 18px;
                    background-color: #1E88E5;
                    border-radius: 15px;
                }
                QPushButton#fullReportButton:hover {
                    background-color: #1565C0;
                }
                QComboBox {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 2px solid #2196F3;
                    padding: 8px;
                    border-radius: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QComboBox:hover {
                    border-color: #1976D2;
                    background-color: #353535;
                }
                QComboBox::drop-down {
                    border: none;
                    background: #2b2b2b;
                }
                QComboBox::down-arrow {
                    image: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    selection-background-color: #2196F3;
                    selection-color: #ffffff;
                    border: 1px solid #454545;
                }
                QComboBox QAbstractItemView::item {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #353535;
                }
                QDateEdit {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 2px solid #2196F3;
                    padding: 8px;
                    border-radius: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QDateEdit:hover {
                    border-color: #1976D2;
                    background-color: #353535;
                }
                QDateEdit::drop-down {
                    border: none;
                    background: #2b2b2b;
                }
                QDateEdit::down-arrow {
                    image: none;
                }
                QCalendarWidget {
                    background-color: #2b2b2b;
                }
                QCalendarWidget QTableView {
                    background-color: #2b2b2b;
                    color: white;
                    selection-background-color: #2196F3;
                    selection-color: white;
                    alternate-background-color: #353535;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: white;
                    background-color: #2b2b2b;
                    selection-background-color: #2196F3;
                    selection-color: white;
                }
                QCalendarWidget QAbstractItemView:disabled {
                    color: #666666;
                }
                QCalendarWidget QWidget {
                    alternate-background-color: #353535;
                    background-color: #2b2b2b;
                }
                QCalendarWidget QToolButton {
                    color: white;
                    background-color: #2b2b2b;
                    border: none;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: #353535;
                    border: none;
                }
                QCalendarWidget QSpinBox {
                    color: white;
                    background-color: #2b2b2b;
                    selection-background-color: #2196F3;
                    selection-color: white;
                }
                QCalendarWidget QMenu {
                    color: white;
                    background-color: #2b2b2b;
                }
                QCalendarWidget QMenu::item:selected {
                    background-color: #2196F3;
                }
                QCalendarWidget #qt_calendar_navigationbar {
                    background-color: #2b2b2b;
                }
                QCalendarWidget #qt_calendar_prevmonth {
                    qproperty-icon: none;
                    color: white;
                }
                QCalendarWidget #qt_calendar_nextmonth {
                    qproperty-icon: none;
                    color: white;
                }
                QCalendarWidget #qt_calendar_monthbutton {
                    color: white;
                }
                QCalendarWidget #qt_calendar_yearbutton {
                    color: white;
                }
                QWidget#periodGroup, QWidget#categoryGroup {
                    background-color: #353535;
                    border-radius: 20px;
                    padding: 25px;
                    border: 1px solid #454545;
                    margin: 10px;
                }
                QWidget#datesWidget {
                    background: transparent;
                }
                QTextEdit#reportText {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #454545;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: monospace;
                }
            """
        else:
            base_style = """
                QWidget {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #2C3E50;
                }
                QLabel#pageTitle {
                    font-size: 32px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: 10px;
                    background: transparent;
                }
                QLabel#sectionTitle {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: 5px;
                    background: transparent;
                }
                QLabel#fieldLabel, QLabel#dateLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #34495E;
                    padding: 5px;
                    background: transparent;
                }
                QPushButton#reportButton, QPushButton#fullReportButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    min-width: 200px;
                }
                QPushButton#reportButton:hover, QPushButton#fullReportButton:hover {
                    background-color: #1976D2;
                }
                QPushButton#reportButton:pressed, QPushButton#fullReportButton:pressed {
                    background-color: #1565C0;
                }
                QPushButton#fullReportButton {
                    font-size: 18px;
                    background-color: #1E88E5;
                    border-radius: 15px;
                }
                QPushButton#fullReportButton:hover {
                    background-color: #1565C0;
                }
                QComboBox {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 2px solid #2196F3;
                    padding: 8px;
                    border-radius: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QComboBox:hover {
                    border-color: #1976D2;
                    background-color: #F5F5F5;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                    border: 1px solid #BDBDBD;
                }
                QDateEdit {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 2px solid #2196F3;
                    padding: 8px;
                    border-radius: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QDateEdit:hover {
                    border-color: #1976D2;
                    background-color: #F5F5F5;
                }
                QDateEdit::drop-down {
                    border: none;
                }
                QDateEdit::down-arrow {
                    image: none;
                }
                QCalendarWidget {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                }
                QCalendarWidget QTableView {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                    alternate-background-color: #F5F5F5;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: #2C3E50;
                    background-color: #FFFFFF;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                }
                QCalendarWidget QAbstractItemView:disabled {
                    color: #666666;
                }
                QCalendarWidget QWidget {
                    alternate-background-color: #F5F5F5;
                    background-color: #FFFFFF;
                }
                QCalendarWidget QToolButton {
                    color: #2C3E50;
                    background-color: #FFFFFF;
                    border: none;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: #F5F5F5;
                    border: none;
                }
                QCalendarWidget QSpinBox {
                    color: #2C3E50;
                    background-color: #FFFFFF;
                    selection-background-color: #2196F3;
                    selection-color: #FFFFFF;
                }
                QCalendarWidget QMenu {
                    color: #2C3E50;
                    background-color: #FFFFFF;
                }
                QCalendarWidget QMenu::item:selected {
                    background-color: #2196F3;
                }
                QCalendarWidget #qt_calendar_navigationbar {
                    background-color: #FFFFFF;
                }
                QCalendarWidget #qt_calendar_prevmonth {
                    qproperty-icon: none;
                    color: #2C3E50;
                }
                QCalendarWidget #qt_calendar_nextmonth {
                    qproperty-icon: none;
                    color: #2C3E50;
                }
                QCalendarWidget #qt_calendar_monthbutton {
                    color: #2C3E50;
                }
                QCalendarWidget #qt_calendar_yearbutton {
                    color: #2C3E50;
                }
                QWidget#periodGroup, QWidget#categoryGroup {
                    background-color: #FFFFFF;
                    border-radius: 20px;
                    padding: 25px;
                    border: 2px solid #E0E0E0;
                    margin: 10px;
                }
                QWidget#datesWidget {
                    background: transparent;
                }
                QTextEdit#reportText {
                    background-color: #ffffff;
                    color: #2C3E50;
                    border: 1px solid #BDBDBD;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: monospace;
                }
            """
        self.setStyleSheet(base_style) 