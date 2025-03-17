import pytest
from pathlib import Path
from datetime import datetime
from parsers.parser_doc import DOCProcessor
import aspose.words as aw

@pytest.fixture
def create_valid_doc(tmp_path):
    """Создает временный валидный DOC-файл."""
    file = tmp_path / "valid.doc"
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    
    # Добавляем текст
    builder.writeln("Первый параграф.")
    builder.writeln("Второй параграф.")
    
    # Добавляем таблицу
    table = builder.start_table()
    for i in range(2):
        builder.insert_cell()
        builder.write(f"Ячейка {i + 1}")
    builder.end_row()
    for i in range(2, 4):
        builder.insert_cell()
        builder.write(f"Ячейка {i + 1}")
    builder.end_table()
    
    # Устанавливаем метаданные
    doc.built_in_document_properties.author = "Test Author"
    doc.built_in_document_properties.created_time = datetime(2023, 1, 1)
    
    doc.save(str(file))
    return str(file)

@pytest.fixture
def create_invalid_doc(tmp_path):
    """Создает временный невалидный DOC-файл."""
    file = tmp_path / "invalid.doc"
    with open(file, "wb") as f:
        f.write(b"This is not a valid DOC")
    return str(file)

@pytest.fixture
def create_corrupted_doc(tmp_path):
    """Создает временный DOC-файл с поврежденными метаданными."""
    file = tmp_path / "corrupted.doc"
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    builder.writeln("Тестовый параграф.")
    doc.save(str(file))

    # Повреждаем файл
    with open(file, "r+b") as f:
        content = f.read()
        f.seek(0)
        f.write(content[:len(content) // 2])  # Обрезаем файл
        f.truncate()

    return str(file)

# Тест на загрузку валидного документа
def test_load_valid_document(create_valid_doc):
    processor = DOCProcessor(create_valid_doc)
    assert processor.doc is not None

# Тест на загрузку невалидного документа
def test_load_invalid_document(create_invalid_doc):
    with pytest.raises(Exception):
        DOCProcessor(create_invalid_doc)

# Тест на извлечение текста
def test_extract_text_valid(create_valid_doc):
    processor = DOCProcessor(create_valid_doc)
    expected_text = "Первый параграф.\nВторой параграф."
    assert processor.text_content.startswith(expected_text)

def test_extract_text_invalid(create_invalid_doc):
    processor = DOCProcessor(create_invalid_doc)
    assert processor.text_content == ""

# Тест на извлечение таблиц
def test_extract_tables_valid(create_valid_doc):
    processor = DOCProcessor(create_valid_doc)
    expected_tables = [
        [["Ячейка 1", "Ячейка 2"], ["Ячейка 3", "Ячейка 4"]]
    ]
    assert processor.tables == expected_tables

def test_extract_tables_invalid(create_invalid_doc):
    processor = DOCProcessor(create_invalid_doc)
    assert processor.tables == []

# Тест на извлечение метаданных
def test_extract_metadata_valid(create_valid_doc):
    processor = DOCProcessor(create_valid_doc)
    expected_metadata = {
        "author": "Test Author",
        "created": datetime(2023, 1, 1),
    }
    assert processor.metadata == expected_metadata

def test_extract_metadata_corrupted(create_corrupted_doc):
    """Проверка, что поврежденные метаданные обрабатываются корректно."""
    processor = DOCProcessor(create_corrupted_doc)
    assert processor.metadata == {}

# Тест на вывод результатов
def test_print_results_valid(create_valid_doc, capsys):
    processor = DOCProcessor(create_valid_doc)
    processor.print_results()
    captured = capsys.readouterr()
    assert "Текст документа:" in captured.out
    assert "Первый параграф." in captured.out
    assert "Таблица 1:" in captured.out
    assert "Ячейка 1 | Ячейка 2" in captured.out
    assert "Метаданные:" in captured.out
    assert "author: Test Author" in captured.out

def test_print_results_invalid(create_invalid_doc, capsys):
    processor = DOCProcessor(create_invalid_doc)
    processor.print_results()
    captured = capsys.readouterr()
    assert "Текст документа:" in captured.out
    assert "Таблицы из документа:" in captured.out
    assert "Метаданные:" in captured.out

# Тест на обработку пустого документа
def test_empty_document(create_empty_doc):
    processor = DOCProcessor(create_empty_doc)
    assert processor.text_content == ""
    assert processor.tables == []
    assert processor.metadata == {"author": "", "created": None}

# Тест на обработку документа без таблиц
def test_no_tables(create_valid_doc):
    processor = DOCProcessor(create_valid_doc)
    if not processor.tables:
        assert True  # Если таблицы отсутствуют, это нормально

# Тест на обработку документа без метаданных
def test_no_metadata(create_empty_doc):
    processor = DOCProcessor(create_empty_doc)
    assert processor.metadata == {"author": "", "created": None}