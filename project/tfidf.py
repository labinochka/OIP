import os
import math
from collections import defaultdict, Counter
import zipfile

PAGES_DIR = "../pages"  # Папка, в которой лежат сохранённые HTML-документы
TOKENS_FILE = "../tokens.txt"  # Файл со списком токенов
LEMMAS_FILE = "../lemmas.txt"  # Файл с леммами и соответствующими токенами

OUTPUT_DIR = "../tfidf_results"  # Файл с леммами и соответствующими токенами
TERMS_DIR = os.path.join(OUTPUT_DIR, "terms")  # Подпапка для терминов
LEMMAS_DIR = os.path.join(OUTPUT_DIR, "lemmas")  # Подпапка для лемм

# Архивы, которые будут созданы
ARCHIVE_TERMS_FILE = "../terms.zip"
ARCHIVE_LEMMAS_FILE = "../lemmas.zip"


# Загрузка токенов
def load_tokens():
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


# Загрузка соответствия token -> lemma
def load_lemma_mapping():
    token_to_lemma = {}
    with open(LEMMAS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            lemma = parts[0]  # лемма
            tokens = parts[1:]  # токены, относящиеся к этой лемме
            for token in tokens:
                token_to_lemma[token] = lemma
    return token_to_lemma


# Создание папок
def create_output_dirs():
    """
        Создаёт папки:
            tfidf_results/
            tfidf_results/terms/
            tfidf_results/lemmas/

        exist_ok=True предотвращает ошибку,
        если папка уже существует.
        """
    os.makedirs(TERMS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)


# Создание архива ZIP с txt файлами
def create_archive(directory, archive_name):
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    print(f"[+] Archive created: {archive_name}")


# Основная функция
def main():
    create_output_dirs()

    tokens_set = load_tokens()
    token_to_lemma = load_lemma_mapping()

    # Хранилища для статистики по документам
    doc_term_counts = {}
    doc_lemma_counts = {}

    # DF (document frequency)
    # сколько документов содержит термин / лемму
    term_df = defaultdict(int)
    lemma_df = defaultdict(int)

    total_docs = 0  # общее количество документов

    # Подсчёт TF и DF
    for filename in os.listdir(PAGES_DIR):
        if filename.endswith(".txt"):

            total_docs += 1
            doc_id = filename.replace(".txt", "")

            with open(os.path.join(PAGES_DIR, filename), "r", encoding="utf-8") as f:
                words = f.read().lower().split()

            # Оставляем только токены из tokens.txt
            words = [w for w in words if w in tokens_set]

            # Общее количество терминов в документе
            total_terms_in_doc = len(words)

            # Подсчёт количества каждого термина
            term_counts = Counter(words)

            # Подсчёт лемм
            lemma_counts = defaultdict(int)
            for term, count in term_counts.items():
                lemma = token_to_lemma.get(term)
                if lemma:
                    lemma_counts[lemma] += count

            # Сохраняем статистику документа
            doc_term_counts[doc_id] = (term_counts, total_terms_in_doc)
            doc_lemma_counts[doc_id] = (lemma_counts, total_terms_in_doc)

            # Обновляем DF терминов
            for term in term_counts:
                term_df[term] += 1

            # Обновляем DF для лемм
            for lemma in lemma_counts:
                lemma_df[lemma] += 1

    # Подсчёт IDF
    # IDF = log(N / df)
    term_idf = {}
    lemma_idf = {}

    for term, df in term_df.items():
        term_idf[term] = math.log(total_docs / df)

    for lemma, df in lemma_df.items():
        lemma_idf[lemma] = math.log(total_docs / df)

    # Вычисление TF-IDF и запись файлов
    # TF = count / total_terms
    # TF-IDF = TF * IDF
    for doc_id in doc_term_counts:

        term_counts, total_terms = doc_term_counts[doc_id]
        lemma_counts, _ = doc_lemma_counts[doc_id]

        # Термины
        term_file_path = os.path.join(TERMS_DIR, f"tfidf_terms_{doc_id}.txt")

        with open(term_file_path, "w", encoding="utf-8") as f:
            for term, count in term_counts.items():
                tf = count / total_terms if total_terms > 0 else 0
                idf = term_idf.get(term, 0)
                tfidf = tf * idf
                f.write(f"{term} {idf:.6f} {tfidf:.6f}\n")

        # Леммы
        lemma_file_path = os.path.join(LEMMAS_DIR, f"tfidf_lemmas_{doc_id}.txt")

        with open(lemma_file_path, "w", encoding="utf-8") as f:
            for lemma, count in lemma_counts.items():
                tf = count / total_terms if total_terms > 0 else 0
                idf = lemma_idf.get(lemma, 0)
                tfidf = tf * idf
                f.write(f"{lemma} {idf:.6f} {tfidf:.6f}\n")

    print("TF-IDF успешно рассчитан.")
    print(f"Результаты сохранены в папке: {OUTPUT_DIR}")
    create_archive(TERMS_DIR, ARCHIVE_TERMS_FILE)
    create_archive(LEMMAS_DIR, ARCHIVE_LEMMAS_FILE)


if __name__ == "__main__":
    main()
