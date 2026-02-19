import re
import os
from collections import defaultdict

PAGES_DIR = "../pages"  # Папка с сохранёнными текстовыми документами
PAGE_TERMS_DIR = "../page_terms"  # Файлы с леммами (лемма -> токены)
INDEX_DOCS_FILE = "../index.txt"  # Файл с соответствием doc_id -> URL
INDEX_FILE = "../inverted_index.txt"  # Файл для сохранения инвертированного индекса


def load_token_to_lemma():
    token_to_lemma = {}

    for filename in os.listdir(PAGE_TERMS_DIR):
        if filename.endswith("_lemmas.txt"):

            file_path = os.path.join(PAGE_TERMS_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    lemma = parts[0]
                    tokens = parts[1:]

                    token_to_lemma[lemma] = lemma

                    for token in tokens:
                        token_to_lemma[token] = lemma

    return token_to_lemma



# Загрузка index.txt
def load_doc_urls():
    doc_urls = {}
    with open(INDEX_DOCS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc_id, url = line.strip().split()
            doc_urls[doc_id] = url
    return doc_urls


# Построение инвертированного индекса
def build_inverted_index():
    """
    Создаёт инвертированный индекс:
    lemma -> множество doc_id, где встречается эта лемма
    """

    inverted_index = defaultdict(set)

    for filename in os.listdir(PAGE_TERMS_DIR):

        # Берём файлы с леммами
        if filename.endswith("_lemmas.txt"):

            # Из имени файла получаем doc_id
            doc_id = filename.split("_")[0]

            file_path = os.path.join(PAGE_TERMS_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()

                    if not parts:
                        continue

                    lemma = parts[0]  # первая колонка — лемма

                    # Добавляем документ в индекс
                    inverted_index[lemma].add(doc_id)

    return inverted_index



# Сохранение индекса в файл
def save_index(index):
    """
        Сохраняет инвертированный индекс в файл
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
            lemma = token_to_lemma.get(token)

            if lemma:
                docs = index.get(lemma, set())
            else:
                docs = set()

            expression.append(f"set({list(docs)})")

    final_expression = " ".join(expression)

    try:
        result = eval(final_expression)
    except Exception as e:
        print(f"Ошибка в запросе: {e}")
        return set()

    return result




def main():
    # Строим индекс
    index = build_inverted_index()
    save_index(index)

    token_to_lemma = load_token_to_lemma()

    print("[+] Индекс построен и сохранён")

    # Загружаем индекс и URL
    index = load_index()
    doc_urls = load_doc_urls()
    all_docs = set(doc_urls.keys())

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
