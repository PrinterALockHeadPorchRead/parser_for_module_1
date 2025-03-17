import PyPDF2
from PyPDF2.errors import PdfReadError, PageRangeError
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
from tabula.io import TabulaError
from pytesseract import TesseractNotFoundError
from pdf2image import convert_from_path
import pytesseract
import tabula
import pandas as pd
from typing import List

class PDFProcessor:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.is_valid = self._validate_pdf_syntax()
        self.text_content = self._extract_text()
        self.ocr_text = self._extract_text_from_images()
        self.tables = self._extract_tables()

    def _validate_pdf_syntax(self) -> bool:
        """Проверка целостности"""
        try:
            with open(self.file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if reader.is_encrypted:
                    raise ValueError("Файл зашифрован")
                for page in reader.pages:
                    page.extract_text()
            return True
        except FileNotFoundError:
            print(f"Ошибка: файл {self.file_path} не найден")
            return False
            
        except PermissionError:
            print("Ошибка доступа: недостаточно прав для чтения файла")
            return False
            
        except PdfReadError as e:
            print(f"Ошибка структуры PDF: {str(e)}")
            return False
            
        except PageRangeError:
            print("Ошибка: документ не содержит страниц")
            return False
        
        except Exception as e:
            print(f"Непредвиденная ошибка валидации: {str(e)}")
            return False

    def _extract_text(self) -> str:
        """Извлечение текста"""
        if not self.is_valid:
            return ""
            
        try:
            text = ""
            with open(self.file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
            
        except PdfReadError:
            print("Ошибка чтения PDF при извлечении текста")
            return ""
            
        except PageRangeError:
            print("Ошибка: неожиданный диапазон страниц")
            return ""
            
        except Exception as e:
            print(f"Непредвиденная ошибка извлечения текста: {str(e)}")
            return ""

    def _extract_text_from_images(self, dpi: int = 300, lang: str = "rus+eng") -> str:
        """Извлечение такста (OCR)"""
        if not self.is_valid:
            return ""
            
        try:
            images = convert_from_path(self.file_path, dpi=dpi)
            return "\n".join(
                pytesseract.image_to_string(img, lang=lang) for img in images
            ).strip()
            
        except PDFInfoNotInstalledError:
            print("Ошибка: не установлен poppler")
            return ""
            
        except PDFPageCountError as e:
            print(f"Ошибка определения количества страниц: {e}")
            return ""
            
        except TesseractNotFoundError:
            print("Ошибка: не найден Tesseract OCR")
            return ""
            
        except Exception as e:
            print(f"Непредвиденная ошибка OCR: {str(e)}")
            return ""

    def _extract_tables(self) -> List[pd.DataFrame]:
        """Извлечение таблиц"""
        if not self.is_valid:
            return []
            
        try:
            tables = tabula.read_pdf(
                self.file_path,
                pages="all",
                multiple_tables=True,
                java_options="-Dfile.encoding=UTF8"
            )
            return [df for df in tables if not df.empty]
            
        except FileNotFoundError:
            print("Ошибка: не найден Java Runtime для Tabula")
            return []
            
        except TabulaError as e:
            print(f"Ошибка извлечения таблиц: {e}")
            return []
            
        except Exception as e:
            print(f"Непредвиденная ошибка таблиц: {str(e)}")
            return []

    def print_results(self) -> None:
        print(f"Статус: {'Валиден' if self.is_valid else 'Ошибка структуры'}")
        
        print("\nТекст документа:")
        print(self.text_content[:500] + "\n..." if len(self.text_content) > 500 else self.text_content)
        
        print("\nТекст с документа (OCR):")
        print(self.ocr_text[:500] + "\n..." if len(self.ocr_text) > 500 else self.ocr_text)
        
        print("\nТаблицыиз докумета:")
        for i, table in enumerate(self.tables, 1):
            print(f"Таблица {i}:")
            print(table.head().to_string() if not table.empty else "Пустая таблица")