import os
import requests
from bs4 import BeautifulSoup
from langdetect import detect
import time
import zipfile

# Настройки

URLS_FILE = "urls.txt"  # Файл со списком URL для скачивания
OUTPUT_DIR = "pages"  # Папка для сохранения скачанных страниц
INDEX_FILE = "index.txt"  # Файл для записи соответствия номера файла и URL
MIN_PAGES = 100  # Минимальное количество страниц для скачивания
TIMEOUT = 60  # Таймаут запроса в секундах
DELAY = 1  # Задержка между запросами (сек)
ARCHIVE_FILE = "pages.zip"  # Имя архива для сохраненных страниц

# User-Agent нужен, чтобы сервер не блокировал запросы
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


# Проверка, что ответ сервера — HTML
def is_html(response):
    content_type = response.headers.get("Content-Type", "")
    return "text/html" in content_type


# Определение языка страницы
def get_page_language(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    if len(text.strip()) < 200:
        return None
    try:
        return detect(text)
    except:
        return None


# Очистка HTML: удаление JS, CSS и изображений
def remove_js_css_images(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Удаляем теги <script>
    for script in soup.find_all("script"):
        script.decompose()

    # Удаляем теги <link rel="stylesheet">
    for link in soup.find_all("link", rel="stylesheet"):
        link.decompose()

    # Удаляем теги <img>
    for img in soup.find_all("img"):
        img.decompose()

    return str(soup)


# Создание архива ZIP с выкаченными страницами
def create_archive(directory, archive_name):
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    print(f"[+] Archive created: {archive_name}")


def main():
    # Создаём папку для страниц, если её нет
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Читаем список URL из файла
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    saved_count = 0
    base_language = None # Язык первой страницы, чтобы все страницы были одного языка

    # Открываем index.txt для записи соответствия файла и URL
    with open(INDEX_FILE, "w", encoding="utf-8") as index_file:
        for url in urls:
            if saved_count >= MIN_PAGES:
                break

            try:
                response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                if response.status_code != 200:
                    print(f"[!] Status code {response.status_code} for {url}")
                    continue

                if not is_html(response):
                    print(f"[!] Not HTML page for {url}")
                    continue

                html_content = response.text
                page_language = get_page_language(html_content)

                if page_language is None:
                    print(f"[!] Page language not found for {url}")
                    continue

                if base_language is None:
                    base_language = page_language # Запоминаем язык первой страницы

                if page_language != base_language:
                    print(f"[!] Page language mismatch for {url}")
                    continue

                clean_html = remove_js_css_images(html_content)

                # Увеличиваем счётчик сохранённых страниц
                saved_count += 1
                file_path = os.path.join(OUTPUT_DIR, f"{saved_count}.txt")

                # Сохраняем очищенную страницу
                with open(file_path, "w", encoding="utf-8") as page_file:
                    page_file.write(clean_html)

                # Записываем в index.txt номер файла и URL
                index_file.write(f"{saved_count} {url}\n")
                time.sleep(DELAY)

                # Пауза между запросами, чтобы сервер не блокировал
                print(f"[+] Saved {saved_count}: {url}")

            except Exception as e:
                print(f"[!] Error with {url}: {e}")
                continue

    print(f"Сохранено страниц: {saved_count}")

    create_archive(OUTPUT_DIR, ARCHIVE_FILE)


if __name__ == "__main__":
    main()
