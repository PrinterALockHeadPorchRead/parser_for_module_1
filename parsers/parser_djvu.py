import subprocess
import pytesseract
from PIL import Image
import os
from subprocess import CalledProcessError

class DJVUProcessor:
    def __init__(self, file_path: str, lang: str = "rus+eng") -> None:
        self.file_path = file_path
        self.lang = lang
        self.is_valid = self._validate_dependencies()
        self.text_content = self._extract_text()
        self.ocr_text = self._extract_text_ocr() if not self.text_content else ""
        self.metadata = self._extract_metadata()
        self.image_count = 0

    def _validate_dependencies(self) -> bool:
        """Проверка наличия необходимых утилит"""
        required_tools = ["djvutxt", "ddjvu"]
        missing = []
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                missing.append(tool)
        if missing:
            print(f"Ошибка: не найдены утилиты: {', '.join(missing)}")
            return False
        return True

    def _extract_text(self) -> str:
        """Извлечение текста"""
        if not self.is_valid:
            return ""
        try:
            result = subprocess.run(
                ["djvutxt", self.file_path],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            return result.stdout.strip()
        except CalledProcessError as e:
            print(f"Ошибка выполнения djvutxt: {e.stderr.decode()}")
            return ""
            
        except UnicodeDecodeError:
            print("Ошибка кодировки: не удалось декодировать вывод djvutxt")
            return ""
        
        except Exception as e:
            print(f"Непредвиденная ошибка извлечения текста: {str(e)}")
            return ""

    def _extract_text_ocr(self) -> str:
        """Извлечение текста с изображений"""
        if not self.is_valid:
            return ""
        temp_image = "temp.tiff"
        try:
            subprocess.run(["ddjvu", "-format=tiff", self.file_path, temp_image], check=True)
            text = pytesseract.image_to_string(Image.open(temp_image), lang=self.lang)
            return text.strip()
        except (PermissionError, IOError) as e:
            print(f"Ошибка доступа к файлам: {str(e)}")
            return ""
        except CalledProcessError as e:
            print(f"Ошибка конвертации в TIFF: {e.stderr.decode()}")
            return ""           
        except pytesseract.TesseractError as e:
            print(f"Ошибка OCR: {e}")
            return ""
        except Exception as e:
            print(f"Непредвиденная ошибка OCR: {str(e)}")
            return ""
        
        finally:
            if os.path.exists(temp_image):
                try:
                    os.remove(temp_image)
                except PermissionError:
                    print("Предупреждение: не удалось удалить временный файл")

    def _extract_metadata(self) -> str:
        """Получение метаданных"""
        if not self.is_valid:
            return ""
        try:
            result = subprocess.run(
                ["djvudump", self.file_path],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            return result.stdout
        except CalledProcessError as e:
            print(f"Ошибка чтения метаданных: {e.stderr.decode()}")
            return ""
        except UnicodeDecodeError:
            print("Ошибка кодировки: не удалось декодировать метаданные")
            return ""
        except Exception as e:
            print(f"Непредвиденная ошибка метаданных: {str(e)}")
            return ""
        
    def print_results(self) -> None:
        print(f"Статус: {'Валиден' if self.is_valid else 'Ошибка зависимостей'}")
        
        print("\nТекст документа:")
        print(self.text_content[:500] + "\n..." if len(self.text_content) > 500 else self.text_content)
        
        if self.ocr_text:
            print("\nТекст документа (OCR):")
            print(self.ocr_text[:500] + "\n..." if len(self.ocr_text) > 500 else self.ocr_text)
            
        print("\nМетаданные:")
        print(self.metadata[:500] + "\n..." if len(self.metadata) > 500 else self.metadata)