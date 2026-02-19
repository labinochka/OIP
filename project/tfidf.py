import os
import math
from collections import defaultdict, Counter
import zipfile

# Папка с исходными HTML-документами
PAGES_DIR = "../pages"

PAGE_TERMS_DIR = "../page_terms"

# Папка для результатов
OUTPUT_DIR = "../tfidf_results"
TERMS_DIR = os.path.join(OUTPUT_DIR, "terms")
LEMMAS_DIR = os.path.join(OUTPUT_DIR, "lemmas")

ARCHIVE_TERMS_FILE = "../terms.zip"
ARCHIVE_LEMMAS_FILE = "../lemmas.zip"


def create_output_dirs():
    os.makedirs(TERMS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)


def create_archive(directory, archive_name):
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    print(f"[+] Archive created: {archive_name}")


# Загрузка токенов страницы
def load_page_tokens(doc_id):
    file_path = os.path.join(PAGE_TERMS_DIR, f"{doc_id}_tokens.txt")

    tokens = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            tokens = [line.strip() for line in f]

    return tokens


# Загрузка лемм страницы
def load_page_lemmas(doc_id):
    file_path = os.path.join(PAGE_TERMS_DIR, f"{doc_id}_lemmas.txt")

    lemma_to_tokens = defaultdict(list)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue

                lemma = parts[0]
                tokens = parts[1:]
                lemma_to_tokens[lemma].extend(tokens)

    return lemma_to_tokens


def main():
    create_output_dirs()

    doc_term_counts = {}
    doc_lemma_counts = {}

    term_df = defaultdict(int)
    lemma_df = defaultdict(int)

    total_docs = 0

    # Обработка каждой страницы
    for filename in os.listdir(PAGES_DIR):

        if filename.endswith(".txt"):

            total_docs += 1
            doc_id = filename.replace(".txt", "")

            # Загружаем токены страницы
            tokens = load_page_tokens(doc_id)

            # Загружаем леммы страницы
            lemma_to_tokens = load_page_lemmas(doc_id)

            # Читаем оригинальный текст страницы
            with open(os.path.join(PAGES_DIR, filename), "r", encoding="utf-8") as f:
                words = f.read().lower().split()

            # Оставляем только токены этой страницы
            words = [w for w in words if w in tokens]

            total_terms_in_doc = len(words)

            # TF терминов
            term_counts = Counter(words)

            # TF лемм
            lemma_counts = defaultdict(int)

            for lemma, lemma_tokens in lemma_to_tokens.items():
                for token in lemma_tokens:
                    lemma_counts[lemma] += term_counts.get(token, 0)

            doc_term_counts[doc_id] = (term_counts, total_terms_in_doc)
            doc_lemma_counts[doc_id] = (lemma_counts, total_terms_in_doc)

            # DF терминов
            for term in term_counts:
                term_df[term] += 1

            # DF лемм
            for lemma in lemma_counts:
                lemma_df[lemma] += 1

    # Подсчёт IDF
    term_idf = {}
    lemma_idf = {}

    for term, df in term_df.items():
        term_idf[term] = math.log(total_docs / df)

    for lemma, df in lemma_df.items():
        lemma_idf[lemma] = math.log(total_docs / df)

    # Запись TF-IDF файлов
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
