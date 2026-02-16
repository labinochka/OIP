import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict


# Настройки

PAGES_DIR = "../pages"  # Папка, в которой лежат сохранённые HTML-документы
TOKENS_FILE = "../tokens.txt"  # Файл для сохранения списка токенов
LEMMAS_FILE = "../lemmas.txt"  # Файл для сохранения сгруппированных лемм

# Стоп-слова
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "of", "at",
    "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there",
    "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just"
}

# Неправильные формы
IRREGULAR_FORMS = {
    "went": "go",
    "gone": "go",
    "did": "do",
    "done": "do",
    "was": "be",
    "were": "be",
    "been": "be",
    "has": "have",
    "had": "have",
    "having": "have",
    "made": "make",
    "took": "take",
    "taken": "take",
    "saw": "see",
    "seen": "see",
    "ran": "run",
    "bought": "buy",
    "brought": "bring",
    "thought": "think",
    "better": "good",
    "best": "good",
    "worse": "bad",
    "worst": "bad"
}

# Функция извлечения текста из HTML
def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ")


# Токенизация
def tokenize(text):
    # Приводим текст к нижнему регистру
    text = text.lower()

    # Регулярное выражение выбирает только слова, состоящие из латинских букв
    tokens = re.findall(r"\b[a-z]+\b", text)

    # Удаляем стоп-слова и слишком короткие слова
    clean_tokens = [
        token for token in tokens
        if token not in STOP_WORDS and len(token) > 2
    ]

    return clean_tokens


# Лемматизация
def smart_lemmatize(word):

    # Неправильные формы
    if word in IRREGULAR_FORMS:
        return IRREGULAR_FORMS[word]

    # Множественное число (companies → company)
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"

    # Множественное число (boxes → box)
    if word.endswith("es") and len(word) > 4:
        return word[:-2]

    # Обычное множественное число (cats → cat)
    if word.endswith("s") and len(word) > 3:
        return word[:-1]

    # Continuous (running → run)
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]

        # Обработка удвоенной согласной (running → run)
        if len(base) > 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base

    # Прошедшее время (played → play)
    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]

        # studied → study
        if base.endswith("i"):
            return base[:-1] + "y"
        return base

    # Сравнительная степень (bigger → big)
    if word.endswith("er") and len(word) > 4:
        base = word[:-2]

        # bigger → big
        if base[-1] == base[-2]:
            base = base[:-1]
        return base

    # Превосходная степень (biggest → big)
    if word.endswith("est") and len(word) > 5:
        base = word[:-3]

        if base[-1] == base[-2]:
            base = base[:-1]
        return base

    return word

def main():
    # Множество для хранения уникальных токенов (без дубликатов)
    all_tokens = set()

    # Проходим по всем файлам в папке pages
    for filename in os.listdir(PAGES_DIR):
        file_path = os.path.join(PAGES_DIR, filename)

        if os.path.isfile(file_path):
            text = extract_text_from_html(file_path)
            tokens = tokenize(text)
            all_tokens.update(tokens)

    # Сортируем токены по алфавиту
    sorted_tokens = sorted(all_tokens)

    # Сохранение tokens.txt
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        for token in sorted_tokens:
            f.write(token + "\n")

    print(f"[+] Сохранено {len(sorted_tokens)} токенов")

    # Группировка по леммам
    lemma_dict = defaultdict(list)

    for token in sorted_tokens:
        lemma = smart_lemmatize(token)
        lemma_dict[lemma].append(token)

    # Сохранение lemmas.txt
    # Формат строки: <лемма> <токен1> <токен2> ... <токенN>
    with open(LEMMAS_FILE, "w", encoding="utf-8") as f:
        for lemma in sorted(lemma_dict.keys()):
            tokens_line = " ".join(sorted(lemma_dict[lemma]))
            f.write(f"{lemma} {tokens_line}\n")

    print(f"[+] Сохранено {len(lemma_dict)} лемм")

if __name__ == "__main__":
    main()
