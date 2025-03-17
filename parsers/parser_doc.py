import aspose.words as aw
from aspose.words import exceptions
from typing import List, Dict, Optional, Union

class DOCProcessor:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.doc = self._load_document()
        self.text_content = self._extract_text()
        self.tables = self._extract_tables()
        self.metadata = self._extract_metadata()

    def _load_document(self) -> Optional[aw.Document]:
        """Загрузка документа"""
        try:
            return aw.Document(self.file_path)
        except exceptions.FileCorruptedException:
            print(f"Ошибка: файл {self.file_path} поврежден")
            return None
        except exceptions.UnsupportedFileFormatException:
            print(f"Ошибка: формат файла {self.file_path} не поддерживается")
            return None
        except FileNotFoundError:
            print(f"Ошибка: файл {self.file_path} не найден")
            return None 
        except exceptions.IncorrectPasswordException:
            print("Ошибка: документ защищен паролем")
            return None
        except Exception as e:
            print(f"Непредвиденная ошибка загрузки: {str(e)}")
            return None

    def _extract_text(self) -> str:
        """Извлечение текста"""
        if not self.doc:
                return ""        
        try:
            return "\n".join(
                node.get_text().strip() 
                for node in self.doc.get_child_nodes(aw.NodeType.ANY, True)
            )
                
        except exceptions.InvalidOperationException as e:
                print(f"Ошибка доступа к узлам документа: {e}")
                return ""
                
        except AttributeError:
                print("Ошибка: неожиданная структура документа")
                return ""
        
        except Exception as e:
            print(f"Непредвиденная ошибка извлечения текста: {str(e)}")
            return ""

    def _extract_tables(self) -> List[List[List[str]]]:
        """Извлечение таблиц"""
        if not self.doc:
            return []
        tables = []
        try:
            for table in self.doc.get_child_nodes(aw.NodeType.TABLE, True):
                rows = []
                for row in table.as_table().rows:
                    try:
                        cells = [cell.get_text().strip() for cell in row.cells]
                        rows.append(cells)
                    except exceptions.InvalidOperationException:
                        print("Пропущена поврежденная строка таблицы")
                        continue
                tables.append(rows)
            return tables
            
        except exceptions.InvalidNodeTypeException:
            print("Ошибка: обнаружен неожиданный тип узла при обработке таблиц")
            return []
        
        except Exception as e:
            print(f"Непредвиденная ошибка извлечения таблиц: {str(e)}")
            return []

    def _extract_metadata(self) -> Dict[str, Union[str, int]]:
        """Получение метаданных"""
        if not self.doc:
            return {}
        try:
            return {
                "author": self.doc.built_in_document_properties.author,
                "created": self.doc.built_in_document_properties.created_time
            }
        except exceptions.ArgumentOutOfRangeException:
            print("Ошибка: недопустимое свойство документа")
            return {}
            
        except AttributeError:
            print("Предупреждение: метаданные отсутствуют")
            return {}
        
        except Exception as e:
            print(f"Непредвиденная ошибка метаданных: {str(e)}")
            return {}

    def print_results(self) -> None:
        print("\nТекст документа:")
        print(self.text_content[:500] + "\n..." if len(self.text_content) > 500 else self.text_content)
        
        print("\nТаблицы из документа:")
        for i, table in enumerate(self.tables, 1):
            print(f"Таблица {i}:")
            for row in table:
                print(" | ".join(row))
                
        print("\nМетаданные:")
        for key, value in self.metadata.items():
            print(f"{key}: {value}")