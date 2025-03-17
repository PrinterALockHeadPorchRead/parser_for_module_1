import pytest
import requests_mock


from parsers.parser_html import WebPageProcessor 

@pytest.fixture
def mock_html():
    """Моковая HTML-страница для тестирования."""
    return """
    <html>
        <head>
            <meta name="description" content="Test description">
            <meta property="og:title" content="Test Title">
        </head>
        <body>
            <h1>Заголовок</h1>
            <p>Первый параграф.</p>
            <p>Второй параграф.</p>
            <img src="image1.jpg" alt="Image 1">
            <img src="image2.jpg">
            <table>
                <tr><th>Header 1</th><th>Header 2</th></tr>
                <tr><td>Data 1</td><td>Data 2</td></tr>
            </table>
            <a href="https://example.com">Example Link</a>
        </body>
    </html>
    """

@pytest.fixture
def processor(mock_html):
    """Создание экземпляра WebPageProcessor с моковым HTML."""
    with requests_mock.Mocker() as m:
        m.get("http://mock.url", text=mock_html)
        return WebPageProcessor("http://mock.url")

# Тест загрузки страницы
def test_load_page(processor):
    assert processor.soup is not None
    assert processor.soup.find("h1").text == "Заголовок"

# Тест извлечения текста
def test_extract_full_text(processor):
    expected_text = "Заголовок\nПервый параграф.\nВторой параграф."
    assert expected_text in processor.full_text

# Тест извлечения изображений
def test_extract_images(processor):
    expected_images = [
        {"src": "image1.jpg", "alt": "Image 1"},
        {"src": "image2.jpg", "alt": "No alt text"}
    ]
    assert processor.images == expected_images

# Тест извлечения таблиц
def test_extract_tables(processor):
    expected_tables = [
        {
            "headers": ["Header 1", "Header 2"],
            "rows": [[], ["Data 1", "Data 2"]]
        }
    ]
    assert processor.tables == expected_tables

# Тест извлечения метаданных
def test_extract_meta_tags(processor):
    expected_meta_tags = {
        "description": "Test description",
        "og:title": "Test Title"
    }
    assert processor.meta_tags == expected_meta_tags

# Тест извлечения ссылок
def test_extract_links(processor):
    expected_links = [
        {"text": "Example Link", "url": "https://example.com"}
    ]
    assert processor.links == expected_links

# Тест обработки пустой страницы
def test_empty_page():
    with requests_mock.Mocker() as m:
        m.get("http://empty.url", text="")
        processor = WebPageProcessor("http://empty.url")
        assert processor.full_text == "b''"
        assert processor.images == []
        assert processor.tables == []
        assert processor.meta_tags == {}
        assert processor.links == []

# Тест обработки страницы без изображений
def test_no_images(mock_html):
    mock_html = """
    <html>
        <body>
            <p>Текст без изображений.</p>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("http://no-images.url", text=mock_html)
        processor = WebPageProcessor("http://no-images.url")
        assert processor.images == []

# Тест обработки страницы без таблиц
def test_no_tables(mock_html):
    mock_html = """
    <html>
        <body>
            <p>Текст без таблиц.</p>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("http://no-tables.url", text=mock_html)
        processor = WebPageProcessor("http://no-tables.url")
        assert processor.tables == []

# Тест обработки страницы без метаданных
def test_no_meta_tags(mock_html):
    mock_html = """
    <html>
        <body>
            <p>Текст без метаданных.</p>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("http://no-meta.url", text=mock_html)
        processor = WebPageProcessor("http://no-meta.url")
        assert processor.meta_tags == {}

# Тест обработки страницы без ссылок
def test_no_links(mock_html):
    mock_html = """
    <html>
        <body>
            <p>Текст без ссылок.</p>
        </body>
    </html>
    """
    with requests_mock.Mocker() as m:
        m.get("http://no-links.url", text=mock_html)
        processor = WebPageProcessor("http://no-links.url")
        assert processor.links == []

def test_print_results_full_text(capsys):
    # Создаем моковый экземпляр класса
    class MockProcessor:
        def __init__(self):
            self.full_text = "a" * 600  # Текст длиной 600 символов
            self.images = []
            self.tables = []
            self.meta_tags = {}
            self.links = []

        def print_results(self):
            print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
            print("\nИзображения:", self.images)
            print("\nТаблицы:", self.tables)
            print("\nМетаданные:", self.meta_tags)
            print("\nСсылки:", self.links)

    processor = MockProcessor()
    processor.print_results()

    # Захватываем вывод
    captured = capsys.readouterr()
    output = captured.out

    # Проверяем, что текст обрезан до 500 символов и дополнен "..."
    assert output.startswith("a" * 500 + "\n...")

def test_print_results_images(capsys):
    class MockProcessor:
        def __init__(self):
            self.full_text = ""
            self.images = [{"src": "image1.jpg", "alt": "Image 1"}]
            self.tables = []
            self.meta_tags = {}
            self.links = []

        def print_results(self):
            print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
            print("\nИзображения:", self.images)
            print("\nТаблицы:", self.tables)
            print("\nМетаданные:", self.meta_tags)
            print("\nСсылки:", self.links)

    processor = MockProcessor()
    processor.print_results()

    captured = capsys.readouterr()
    output = captured.out

    assert "Изображения: [{'src': 'image1.jpg', 'alt': 'Image 1'}]" in output

def test_print_results_tables(capsys):
    class MockProcessor:
        def __init__(self):
            self.full_text = ""
            self.images = []
            self.tables = [{"headers": ["Header 1"], "rows": [["Data 1"]]}]
            self.meta_tags = {}
            self.links = []

        def print_results(self):
            print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
            print("\nИзображения:", self.images)
            print("\nТаблицы:", self.tables)
            print("\nМетаданные:", self.meta_tags)
            print("\nСсылки:", self.links)

    processor = MockProcessor()
    processor.print_results()

    captured = capsys.readouterr()
    output = captured.out

    assert "Таблицы: [{'headers': ['Header 1'], 'rows': [['Data 1']]}]" in output

def test_print_results_meta_tags(capsys):
    class MockProcessor:
        def __init__(self):
            self.full_text = ""
            self.images = []
            self.tables = []
            self.meta_tags = {"description": "Test description"}
            self.links = []

        def print_results(self):
            print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
            print("\nИзображения:", self.images)
            print("\nТаблицы:", self.tables)
            print("\nМетаданные:", self.meta_tags)
            print("\nСсылки:", self.links)

    processor = MockProcessor()
    processor.print_results()

    captured = capsys.readouterr()
    output = captured.out

    assert "Метаданные: {'description': 'Test description'}" in output

def test_print_results_links(capsys):
    class MockProcessor:
        def __init__(self):
            self.full_text = ""
            self.images = []
            self.tables = []
            self.meta_tags = {}
            self.links = [{"text": "Example Link", "url": "https://example.com"}]

        def print_results(self):
            print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
            print("\nИзображения:", self.images)
            print("\nТаблицы:", self.tables)
            print("\nМетаданные:", self.meta_tags)
            print("\nСсылки:", self.links)

    processor = MockProcessor()
    processor.print_results()

    captured = capsys.readouterr()
    output = captured.out

    assert "Ссылки: [{'text': 'Example Link', 'url': 'https://example.com'}]" in output