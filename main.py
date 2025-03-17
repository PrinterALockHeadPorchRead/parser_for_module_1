import argparse
from pathlib import Path
from urllib.parse import urlparse
from requests.exceptions import RequestException
from typing import Union
from typing import Union, Optional
import sys

from parsers.parser_html import WebPageProcessor 
from parsers.parser_pdf import PDFProcessor  
from parsers.parser_djvu import DJVUProcessor 
from parsers.parser_doc import DOCProcessor  
from parsers.parser_docx import DOCXProcessor 

class FileProcessor:
    def __init__(self, input_path: str) -> None:
        self.input_path = input_path
        self.processor: Optional[
            Union[
                WebPageProcessor, 
                PDFProcessor, 
                DJVUProcessor, 
                DOCProcessor, 
                DOCXProcessor
            ]
        ] = None
        self.is_url: bool = False
        
        try:
            self.is_url = self._is_valid_url(input_path)
            self.processor = self._get_processor()
        except (FileNotFoundError, ValueError) as e:
            print(f"Ошибка инициализации: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Непредвиденная ошибка: {str(e)}")
            sys.exit(1)

    def _is_valid_url(self, path: str) -> bool:
        """Проверка существования URL"""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError as e:
            print(f"Ошибка формата URL: {e}")
            return False
        except Exception as e:
            print(f"Непредвиденная ошибка проверки URL: {str(e)}")
            return False

    def _get_processor(self) -> Union[
        WebPageProcessor, PDFProcessor, DJVUProcessor, DOCProcessor, DOCXProcessor
    ]:
        """Выбор обработчика в зависимости от формата входа"""
        try:
            if self.is_url:
                return WebPageProcessor(self.input_path)
                
            file_path = Path(self.input_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Файл {file_path} не найден")
                
            ext = file_path.suffix.lower()
            match ext:
                case '.html':
                    return WebPageProcessor(self.input_path)
                case '.pdf':
                    return PDFProcessor(self.input_path)
                case '.djvu':
                    return DJVUProcessor(self.input_path)
                case '.doc':
                    return DOCProcessor(self.input_path)
                case '.docx':
                    return DOCXProcessor(self.input_path)
                case _:
                    raise ValueError(f"Неподдерживаемый формат: {ext}")
                    
        except PermissionError:
            print(f"Ошибка доступа: недостаточно прав для {self.input_path}")
            raise
        except (FileNotFoundError, ValueError) as e:
            print(str(e))
            raise
        except Exception as e:
            print(f"Ошибка создания процессора: {str(e)}")
            raise

    def process(self) -> None:
        """Собственно парсинг"""
        if not self.processor:
            print("Ошибка: процессор не инициализирован")
            return
            
        try:
            print(f"\nОбработка: {self.input_path}")
            self.processor.print_results()
            
        except RequestException as e:
            print(f"Сетевая ошибка при обработке: {str(e)}")
        except (PDFProcessor.exceptions.PdfReadError, 
                DOCXProcessor.exceptions.InvalidFileFormatError) as e:
            print(f"Ошибка формата документа: {str(e)}")
        except Exception as e:
            print(f"Непредвиденная ошибка обработки: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Синтаксический анализатори html страниц, документов форматов .pdf, .doc, .docx, .djvu")
    parser.add_argument("input_path", help="Путь к файлу или URL для парсинга")
    args = parser.parse_args()

    try:
        processor = FileProcessor(args.input_path)
        processor.process()
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)