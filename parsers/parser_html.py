import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Union

class WebPageProcessor:
    def __init__(self, url: str) -> None:
        self.url = url
        self.soup = self._load_page()
        self.full_text = self._extract_full_text()
        self.images = self._extract_images()
        self.tables = self._extract_tables()
        self.meta_tags = self._extract_meta_tags()
        self.links = self._extract_links()

    def _load_page(self) -> BeautifulSoup:
        """Загрузка страницы html"""
        response = requests.get(self.url)
        return BeautifulSoup(response.content, "html.parser") 

    def _extract_full_text(self) -> str:
        """Извлечение текста"""
        return self.soup.get_text(separator="\n", strip=True)

    def _extract_images(self) -> List[Dict[str, str]]:
        """Извлечение изображений"""
        images = []
        for img in self.soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "No alt text")
            images.append({"src": src, "alt": alt})
        return images

    def _extract_tables(self) -> List[Dict[str, Union[List[str], List[List[str]]]]]:
        """Извлечение таблиц"""
        tables = []
        for table in self.soup.find_all("table"):
            headers = [th.text.strip() for th in table.find_all("th")]
            rows = []
            for row in table.find_all("tr"):
                cells = [td.text.strip() for td in row.find_all("td")]
                rows.append(cells)
            tables.append({"headers": headers, "rows": rows})
        return tables

    def _extract_meta_tags(self) -> Dict[str, str]:
        """Извлечние метаданных"""
        meta_tags = {}
        for meta in self.soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                meta_tags[name] = content
        return meta_tags

    def _extract_links(self) -> List[Dict[str, str]]:
        """Извлечение ссылок"""
        links = []
        for a in self.soup.find_all("a", href=True):
            links.append({
                "text": a.text.strip(),
                "url": a["href"]
            })
        return links

    def print_results(self) -> None:
        print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
        print("\nИзображения:", self.images)
        print("\nТаблицы:", self.tables)
        print("\nМетаданные:", self.meta_tags)
        print("\nСсылки:", self.links)