import requests
from bs4 import BeautifulSoup, FeatureNotFound
from typing import List, Dict, Union
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError

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
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            try:
                return BeautifulSoup(response.content, "html.parser")
            except FeatureNotFound:
                print("Ошибка: не найден парсер 'html.parser'")
                return None
                
        except ConnectionError:
            print(f"Ошибка подключения к {self.url}")
            return None
            
        except Timeout:
            print(f"Таймаут при загрузке {self.url}")
            return None
            
        except HTTPError as e:
            print(f"HTTP ошибка {e.response.status_code}: {e.response.reason}")
            return None
            
        except RequestException as e:
            print(f"Непредвиденная сетевая ошибка: {str(e)}")
            return None

    def _extract_full_text(self) -> str:
        """Извлечение текста"""
        if not self.soup:
            return ""
            
        try:
            return self.soup.get_text(separator="\n", strip=True)
            
        except AttributeError:
            print("Ошибка: неожиданная структура HTML")
            return ""
        except Exception as e:
            print(f"Непредвиденная ошибка извлечения текста: {str(e)}")
            return ""

    def _extract_images(self) -> List[Dict[str, str]]:
        """Извлечение изображений"""
        if not self.soup:
            return []
            
        images = []
        try:
            for img in self.soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "No alt text")
                images.append({"src": src, "alt": alt})
            return images
            
        except AttributeError:
            print("Ошибка: неожиданная структура тега img")
            return []
        except Exception as e:
            print(f"Непредвиденная ошибка изображений: {str(e)}")
            return []

    def _extract_tables(self) -> List[Dict[str, Union[List[str], List[List[str]]]]]:
        """Извлечение таблиц"""
        if not self.soup:
            return []
            
        tables = []
        try:
            for table in self.soup.find_all("table"):
                headers = []
                rows = []
                try:
                    headers = [th.text.strip() for th in table.find_all("th")]
                except AttributeError:
                    print("Предупреждение: пропущены заголовки таблицы")
                    
                for row in table.find_all("tr"):
                    try:
                        cells = [td.text.strip() for td in row.find_all("td")]
                        rows.append(cells)
                    except AttributeError:
                        print("Пропущена поврежденная строка таблицы")
                        continue
                tables.append({"headers": headers, "rows": rows})
            return tables
            
        except AttributeError:
            print("Ошибка: неожиданная структура таблицы")
            return []
        except Exception as e:
            print(f"Непредвиденная ошибка таблиц: {str(e)}")
            return []

    def _extract_meta_tags(self) -> Dict[str, str]:
        """Извлечние метаданных"""
        if not self.soup:
            return {}
            
        meta_tags = {}
        try:
            for meta in self.soup.find_all("meta"):
                name = meta.get("name") or meta.get("property")
                content = meta.get("content")
                if name and content:
                    meta_tags[name] = content
            return meta_tags
            
        except AttributeError:
            print("Ошибка: неожиданная структура meta-тегов")
            return {}
        except Exception as e:
            print(f"Непредвиденная ошибка метатегов: {str(e)}")
            return {}

    def _extract_links(self) -> List[Dict[str, str]]:
        """Извлечение ссылок"""
        if not self.soup:
            return []
            
        links = []
        try:
            for a in self.soup.find_all("a", href=True):
                text = a.text.strip()
                url = a.get("href", "")
                links.append({"text": text, "url": url})
            return links
            
        except AttributeError:
            print("Ошибка: неожиданная структура ссылок")
            return []
        except Exception as e:
            print(f"Непредвиденная ошибка ссылок: {str(e)}")
            return []

    def print_results(self) -> None:
        print(self.full_text[:500] + "\n..." if len(self.full_text) > 500 else self.full_text)
        print("\nИзображения:", self.images)
        print("\nТаблицы:", self.tables)
        print("\nМетаданные:", self.meta_tags)
        print("\nСсылки:", self.links)