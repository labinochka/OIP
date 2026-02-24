from flask import Flask, render_template, request
from vector_search import search, load_document_vectors, load_doc_urls

app = Flask(__name__)

# Загружаем данные при старте
doc_urls = load_doc_urls()
doc_vectors, idf_values = load_document_vectors()


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            search_results = search(query, doc_vectors, idf_values)
            # Берём топ 10
            results = [(doc_urls.get(doc_id, "URL не найден"), score)
                       for doc_id, score in search_results[:10]]

    return render_template("index.html", query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
