import pytest
from pathlib import Path
from unittest.mock import patch
from PyPDF2 import PdfWriter
from pypdf import PdfReader
import pytesseract


from parsers.parser_pdf import PDFProcessor  

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@pytest.fixture
def tmp_pdf(tmp_path):
    file = tmp_path / "valid.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(file, "wb") as f:
        writer.write(f)
    return str(file)

# Тест на валидацию корректного PDF-файла
def test_validate_pdf_syntax_valid(tmp_pdf):
    """Проверка, что валидный PDF распознается как корректный."""
    processor = PDFProcessor(tmp_pdf)
    assert processor.is_valid is True

# Тест на валидацию невалидного PDF-файла
def test_validate_pdf_syntax_invalid(tmp_path):
    """Проверка, что невалидный PDF не проходит валидацию."""
    file = tmp_path / "invalid.pdf"
    file.write_text("This is not a PDF")  # Невалидный файл
    processor = PDFProcessor(str(file))
    assert processor.is_valid is False

# Тест на извлечение текста из пустого PDF
def test_extract_text_valid_pdf(tmp_pdf):
    """Проверка, что текст извлекается корректно (пустой PDF)."""
    processor = PDFProcessor(tmp_pdf)
    assert processor.text_content == ""  # Пустой PDF без текста

# Тест на извлечение текста из зашифрованного PDF
@patch("PyPDF2.PdfReader.is_encrypted", True)
def test_extract_text_encrypted_pdf(tmp_pdf):
    """Проверка, что зашифрованный PDF не возвращает текст."""
    processor = PDFProcessor(tmp_pdf)
    assert processor.text_content == ""


# Тест на извлечение текста через OCR
@patch("pytesseract.image_to_string", return_value="Extracted OCR text")
def test_extract_ocr_text_from_scanned_pdf(mock_tesseract, tmp_pdf):
    """Проверка, что OCR корректно извлекает текст."""
    processor = PDFProcessor(tmp_pdf)
    assert "Extracted OCR text" in processor.ocr_text

# Тест на извлечение таблиц из PDF
def test_extract_tables_valid_pdf(tmp_pdf):
    """Проверка, что таблицы извлекаются как список."""
    processor = PDFProcessor(tmp_pdf)
    assert isinstance(processor.tables, list)  # Должен быть список таблиц

# Тест на отсутствие таблиц в PDF
def test_extract_tables_no_tables(tmp_pdf):
    """Проверка, что при отсутствии таблиц возвращается пустой список."""
    processor = PDFProcessor(tmp_pdf)
    assert processor.tables == []

# Тест на обработку большого PDF-файла
def test_large_pdf_file(tmp_path):
    """Проверка, что большой PDF обрабатывается корректно."""
    file = tmp_path / "large.pdf"
    with open(file, "wb") as f:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        for _ in range(100):  # Создаем PDF с 100 страницами
            writer.add_blank_page(width=72, height=72)
        writer.write(f)
    processor = PDFProcessor(str(file))
    assert processor.is_valid is True
    assert len(processor.text_content) == 0  # Пустой PDF без текста

# Тест на обработку поврежденного PDF-файла
def test_corrupted_pdf_file(tmp_path):
    """Проверка, что поврежденный PDF не вызывает ошибок."""
    file = tmp_path / "corrupted.pdf"
    file.write_bytes(b"%PDF-1.4\n%EOF")  # Неполный PDF
    processor = PDFProcessor(str(file))
    assert processor.is_valid is False
    assert processor.text_content == ""
    assert processor.ocr_text == ""
    assert processor.tables == []

# Тест на попытку обработать несуществующий файл
def test_nonexistent_file():
    """Проверка, что несуществующий файл вызывает FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PDFProcessor("nonexistent.pdf")
