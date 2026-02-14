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

## 5. Запуск краулера
``python crawler.py``

## 6. Запуск токенизации и лемматизации
``python text_processing.py``

