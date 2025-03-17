import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from parsers.parser_djvu import DJVUProcessor
import subprocess
import pytesseract
from PIL import Image


@pytest.fixture
def create_valid_djvu(tmp_path):
    """Создает временный валидный DJVU-файл."""
    file = tmp_path / "valid.djvu"
    with open(file, "wb") as f:
        f.write(b"Dummy DJVU content")
    return str(file)

@pytest.fixture
def create_invalid_djvu(tmp_path):
    """Создает временный невалидный DJVU-файл."""
    file = tmp_path / "invalid.djvu"
    with open(file, "wb") as f:
        f.write(b"This is not a valid DJVU")
    return str(file)

@pytest.fixture
def mock_dependencies():
    """Мокирует зависимости (djvutxt, ddjvu, djvudump) для успешного выполнения."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="Version 1.2", returncode=0),  # djvutxt --version
            MagicMock(stdout="Version 1.3", returncode=0),  # ddjvu --version
            MagicMock(stdout="Version 1.4", returncode=0),  # djvudump --version
        ]
        yield mock_run

@pytest.fixture
def mock_missing_dependencies():
    """Мокирует отсутствие зависимостей."""
    with patch("subprocess.run", side_effect=FileNotFoundError("Command not found")):
        yield

# Тест на извлечение текста
def test_extract_text_valid(create_valid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stdout="Extracted text from djvutxt", returncode=0)
    ]
    processor = DJVUProcessor(create_valid_djvu)
    assert processor.text_content == "Extracted text from djvutxt"

def test_extract_text_invalid(create_invalid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stderr="Error extracting text", returncode=1)
    ]
    processor = DJVUProcessor(create_invalid_djvu)
    assert processor.text_content == ""

# Тест на извлечение текста с OCR
def test_extract_text_ocr_valid(create_valid_djvu):
    with patch("pytesseract.image_to_string", return_value="OCR extracted text"):
        processor = DJVUProcessor(create_valid_djvu, lang="eng")
        assert processor.ocr_text == "OCR extracted text"

def test_extract_text_ocr_error(create_valid_djvu):
    with patch("pytesseract.image_to_string", side_effect=Exception("OCR error")):
        processor = DJVUProcessor(create_valid_djvu, lang="eng")
        assert processor.ocr_text == ""

# Тест на извлечение метаданных
def test_extract_metadata_valid(create_valid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stdout="Metadata from djvudump", returncode=0)
    ]
    processor = DJVUProcessor(create_valid_djvu)
    assert processor.metadata == "Metadata from djvudump"

def test_extract_metadata_invalid(create_invalid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stderr="Error extracting metadata", returncode=1)
    ]
    processor = DJVUProcessor(create_invalid_djvu)
    assert processor.metadata == ""

# Тест на вывод результатов
def test_print_results_valid(create_valid_djvu, mock_dependencies, capsys):
    mock_dependencies.side_effect = [
        MagicMock(stdout="Extracted text", returncode=0),
        MagicMock(stdout="Metadata", returncode=0)
    ]
    processor = DJVUProcessor(create_valid_djvu)
    processor.print_results()
    captured = capsys.readouterr()
    assert "Статус: Валиден" in captured.out
    assert "Текст документа:" in captured.out
    assert "Extracted text" in captured.out
    assert "Метаданные:" in captured.out
    assert "Metadata" in captured.out

def test_print_results_invalid(create_invalid_djvu, capsys):
    processor = DJVUProcessor(create_invalid_djvu)
    processor.print_results()
    captured = capsys.readouterr()
    assert "Статус: Ошибка зависимостей" in captured.out
    assert "Текст документа:" in captured.out
    assert "Метаданные:" in captured.out

# Тест на обработку несуществующего файла
def test_nonexistent_file():
    """Проверка, что несуществующий файл вызывает исключение."""
    with pytest.raises(FileNotFoundError):
        DJVUProcessor("nonexistent.djvu")

# Тест на обработку пустого документа
def test_empty_document(tmp_path):
    """Проверка обработки пустого документа."""
    file = tmp_path / "empty.djvu"
    file.touch()  # Создаем пустой файл
    processor = DJVUProcessor(str(file))
    assert processor.text_content == ""
    assert processor.ocr_text == ""
    assert processor.metadata == ""

# Тест на обработку документа без текста
def test_no_text(create_valid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stdout="", returncode=0)  # djvutxt возвращает пустой текст
    ]
    processor = DJVUProcessor(create_valid_djvu)
    assert processor.text_content == ""
    assert processor.ocr_text != ""  # OCR должен быть выполнен

# Тест на обработку документа без изображений
def test_no_images(create_valid_djvu, mock_dependencies):
    mock_dependencies.side_effect = [
        MagicMock(stdout="Extracted text", returncode=0),
        subprocess.CalledProcessError(1, "ddjvu")  # ddjvu завершается с ошибкой
    ]
    processor = DJVUProcessor(create_valid_djvu)
    assert processor.ocr_text == ""

# Тест на удаление временного файла после OCR
def test_temp_file_cleanup(create_valid_djvu):
    temp_image = "temp.tiff"
    with patch("os.remove") as mock_remove:
        processor = DJVUProcessor(create_valid_djvu)
        processor._extract_text_ocr()
        mock_remove.assert_called_once_with(temp_image)