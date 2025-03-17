import aspose.words as aw
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
        except Exception as e:
            print(f"Ошибка загрузки документа: {e}")
            return None

    def _extract_text(self) -> str:
        """Извлечение текста"""
        if not self.doc:
            return ""
        return "\n".join(
            node.get_text().strip() 
            for node in self.doc.get_child_nodes(aw.NodeType.ANY, True)
        )

    def _extract_tables(self) -> List[List[List[str]]]:
        """Извлечение таблиц"""
        if not self.doc:
            return []
        tables = []
        for table in self.doc.get_child_nodes(aw.NodeType.TABLE, True):
            rows = []
            for row in table.as_table().rows:
                cells = [cell.get_text().strip() for cell in row.cells]
                rows.append(cells)
            tables.append(rows)
        return tables

    def _extract_metadata(self) -> Dict[str, Union[str, int]]:
        """Получение метаданных"""
        if not self.doc:
            return {}
        try:
            return {
                "author": self.doc.built_in_document_properties.author,
                "created": self.doc.built_in_document_properties.created_time
            }
        except Exception as e:
            print(f"Ошибка извлечения метаданных: {e}")
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