# Deployment Manual

## 1. Системные требования

- Python версии 3.8 или выше
- Доступ к интернету

Проверка версии Python:

``
python --version
``

## 2. Клонирование репозитория
```commandline
git clone https://github.com/labinochka/OIP.git
cd OIP
```

## 3. Создание виртуального окружения (рекомендуется)

Windows:
```commandline
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:
```commandline
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Установка зависимостей
``pip install -r requirements.txt``

## 5. Переход в папку со скриптами
``cd project``

## 6. Запуск краулера
``python crawler.py``

## 7. Запуск токенизации и лемматизации
``python text_processing.py``

## 8. Запуск построения инвертированного индекса и булева поиска
``python boolean_search.py``

## 9. Запуск подсчета TF-IDF
``python tfidf.py``

## 10. Запуск векторного поиска
``python vector_search.py``

