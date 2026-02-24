import os
import math
from collections import defaultdict, Counter

TFIDF_DIR = "../tfidf_results/lemmas"
INDEX_DOCS_FILE = "../index.txt"


# Загрузка doc_id -> URL
def load_doc_urls():
    doc_urls = {}
    with open(INDEX_DOCS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc_id, url = line.strip().split()
            doc_urls[doc_id] = url
    return doc_urls


# Загрузка TF-IDF документов
def load_document_vectors():
    """
    Загружает TF-IDF векторы документов.
    Возвращает:
        doc_vectors[doc_id] = {lemma: tfidf}
        idf_values[lemma] = idf
    """
    doc_vectors = {}
    idf_values = {}

    for filename in os.listdir(TFIDF_DIR):
        if filename.endswith(".txt"):

            doc_id = filename.replace("tfidf_lemmas_", "").replace(".txt", "")
            vector = {}

            with open(os.path.join(TFIDF_DIR, filename), "r", encoding="utf-8") as f:
                for line in f:
                    lemma, idf, tfidf = line.strip().split()
                    vector[lemma] = float(tfidf)
                    idf_values[lemma] = float(idf)

            doc_vectors[doc_id] = vector

    return doc_vectors, idf_values


# Косинусное сходство
def cosine_similarity(vec1, vec2):

    # Скалярное произведение
    dot_product = 0
    for term in vec1:
        if term in vec2:
            dot_product += vec1[term] * vec2[term]

    # Длины векторов
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot_product / (norm1 * norm2)


# Построение вектора запроса
def build_query_vector(query, idf_values):

    words = query.lower().split()
    term_counts = Counter(words)

    total_terms = len(words)
    query_vector = {}

    for term, count in term_counts.items():
        if term in idf_values:
            tf = count / total_terms
            idf = idf_values[term]
            query_vector[term] = tf * idf

    return query_vector


# Поиск
def search(query, doc_vectors, idf_values):

    query_vector = build_query_vector(query, idf_values)

    scores = {}

    for doc_id, doc_vector in doc_vectors.items():
        score = cosine_similarity(query_vector, doc_vector)
        if score > 0:
            scores[doc_id] = score

    # Сортировка по убыванию
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)



def main():

    doc_urls = load_doc_urls()
    doc_vectors, idf_values = load_document_vectors()

    print("Введите запрос или 'exit'.")

    while True:
        query = input("\nЗапрос: ")

        if query.lower() == "exit":
            break

        results = search(query, doc_vectors, idf_values)

        if not results:
            print("Ничего не найдено.")
            continue

        print("\nРезультаты:")
        for doc_id, score in results[:10]:
            print(f"{doc_urls.get(doc_id)} | score={score:.4f}")


if __name__ == "__main__":
    main()
