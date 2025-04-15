import os
import fitz  # PyMuPDF


def create_folder_for_book(book_id, base_folder="data/books"):
    """Создает папку для книги."""
    folder_path = os.path.join(base_folder, str(book_id))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def save_first_page_as_cover(doc, folder_path):
    """Сохраняет первую страницу как обложку."""
    first_page = doc.load_page(0)
    pix = first_page.get_pixmap()
    cover_path = os.path.join(folder_path, "cover.png")
    pix.save(cover_path)
    return cover_path


def save_all_pages(doc, folder_path):
    """Сохраняет все страницы PDF в папку."""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        page_path = os.path.join(folder_path, f"page_{page_num}.png")
        pix.save(page_path)