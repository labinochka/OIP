import re
import os
from collections import defaultdict

PAGES_DIR = "pages" # Папка с сохранёнными текстовыми документами
LEMMAS_FILE = "lemmas.txt" # Файл с леммами (лемма -> токены)
INDEX_DOCS_FILE = "index.txt" # Файл с соответствием doc_id -> URL
INDEX_FILE = "inverted_index.txt" # Файл для сохранения инвертированного индекса


# Загрузка соответствия токен -> лемма
def load_lemma_mapping():
    token_to_lemma = {}
    with open(LEMMAS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            lemma = parts[0] # первая колонка - лемма
            tokens = parts[1:] # остальные слова - токены
            for token in tokens:
                token_to_lemma[token] = lemma
    return token_to_lemma


# Загрузка соответствия doc_id -> URL
def load_doc_urls():
    doc_urls = {}
    with open(INDEX_DOCS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc_id, url = line.strip().split()
            doc_urls[doc_id] = url
    return doc_urls


# Построение инвертированного индекса
def build_inverted_index(token_to_lemma):
    """
        Создаёт инвертированный индекс:
            lemma -> множество doc_id, где встречается эта лемма
        """
    inverted_index = defaultdict(set)

    # Проходим по каждому документу
    for filename in os.listdir(PAGES_DIR):
        # Обрабатываем только текстовые файлы (*.txt)
        if filename.endswith(".txt"):
            # Создаём идентификатор документа, убирая расширение
            doc_id = filename.replace(".txt", "")
            with open(os.path.join(PAGES_DIR, filename), "r", encoding="utf-8") as f:
                # Читаем весь текст, приводим к нижнему регистру и разбиваем на токены
                tokens = f.read().lower().split()
                for token in tokens:
                    # Получаем лемму для токена из словаря token_to_lemma
                    lemma = token_to_lemma.get(token)
                    # Если лемма найдена, добавляем идентификатор документа в инвертированный индекс
                    # Используем set, чтобы один документ не дублировался для одной леммы
                    if lemma:
                        inverted_index[lemma].add(doc_id)

    return inverted_index


# Сохранение индекса в файл
def save_index(index):
    """
        Сохраняет инвертированный индекс в файл inverted_index.txt
        Формат: <лемма> <doc_id1> <doc_id2> ...
        """
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        for lemma in sorted(index.keys()):
            f.write(lemma + " " + " ".join(sorted(index[lemma])) + "\n")


# Загрузка индекса из файла
def load_index():
    index = defaultdict(set)
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            lemma = parts[0]
            docs = parts[1:]
            index[lemma] = set(docs)
    return index


# Булев поиск
def boolean_search(query, index, all_docs, token_to_lemma):

    query = query.lower()
    tokens = re.findall(r"\w+|\(|\)", query)
    expression = []

    for token in tokens:
        if token == "and":
            expression.append("&")
        elif token == "or":
            expression.append("|")
        elif token == "not":
            expression.append("all_docs -")
        elif token in ("(", ")"):
            expression.append(token)
        else:
            # Приводим токен к лемме
            lemma = token_to_lemma.get(token)
            docs = index.get(lemma, set()) if lemma else set()
            # Вставляем множество doc_id для леммы
            expression.append(f"set({list(docs)})")

    final_expression = " ".join(expression)

    try:
        # Выполняем Python-выражение, чтобы вычислить пересечения и объединения
        result = eval(final_expression)
    except Exception as e:
        print(f"Ошибка в запросе: {e}")
        return set()

    return result



def main():
    # Загружаем токен -> лемма
    token_to_lemma = load_lemma_mapping()

    # Строим индекс и сохраняем
    index = build_inverted_index(token_to_lemma)
    save_index(index)
    print("[+] Индекс построен и сохранён")

    # Загружаем индекс и соответствие doc_id -> URL
    index = load_index()
    doc_urls = load_doc_urls()
    all_docs = set(doc_urls.keys()) # нужно для NOT

    print("\nВведите запрос с операторами AND, OR, NOT. Для выхода введите 'exit'.")

    while True:
        query = input("\nЗапрос: ")
        if query.lower() == "exit":
            break

        result = boolean_search(query, index, all_docs, token_to_lemma)

        print("\nНайденные ссылки:")
        if result:
            for doc_id in sorted(result):
                print(doc_urls.get(doc_id, "URL не найден"))
        else:
            print("Ничего не найдено")


if __name__ == "__main__":
    main()
