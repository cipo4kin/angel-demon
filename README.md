# ⚖️ Ангел и Демон (Telegram Mini App)

> Интерактивный Telegram Mini App сервис для разбора жизненных дилемм и принятия взвешенных решений с помощью искусственного интеллекта.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=flat&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57?style=flat&logo=sqlite&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq_API-F55036?style=flat)

---

## 🌟 Возможности проекта

- **🕊 Ангел vs 🔥 Демон**: мгновенная генерация двух полярных взглядов на любую ситуацию (долгосрочная польза и совесть против сиюминутного кайфа и выгоды).
- **🔮 Вердикт Судьи**: глубокий психологический анализ дилеммы, объединяющий обе крайности в практичный компромисс.
- **🎭 Система стилей (Скины)**: возможность переключать характер ответов:
  - *Классический*: строгий философский дуализм;
  - *Офисный душнила*: разбор через KPI, дедлайны и корпоративный сарказм;
  - *Пацанский*: аргументы на кортах по понятиям.
- **⭐ Telegram Stars**: полноценная интеграция официальных платежей Telegram для покупки сфер Судьи и разблокировки кастомных скинов.
- **🛡 Отказоустойчивый пул ключей (Key Pool & Failover)**: бэкенд поддерживает балансировку через список API-ключей Groq с автоматическим повтором при возникновении Rate Limit (`429 Too Many Requests`).
- **🎨 Clean UI Frontend**: легковесный фронтенд на Vanilla JS и кастомном адаптивном CSS без тяжелых внешних библиотек, оформленный по строгим стандартам контрастного темного интерфейса.

---

## 🏗 Архитектура проекта

```text
angel-demon/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI эндпоинты (/dilemma, /choose, /create-invoice)
│   │   ├── database/     # Асинхронные SQL-запросы (aiosqlite) и инициализация схемы
│   │   ├── services/     # Telegram-бот (aiogram 3), пулы Groq LLM и промпты
│   │   ├── config.py     # Валидация переменных окружения (pydantic-settings)
│   │   └── main.py       # Точка входа Uvicorn с асинхронным lifespan
│   ├── requirements.txt  # Зависимости бэкенда
│   └── .env.example      # Пример конфигурации окружения
├── frontend/
│   ├── index.html        # Семантическая разметка Telegram Mini App
│   ├── style.css         # Строгий Clean UI с адаптивной сеткой
│   └── script.js         # Telegram WebApp SDK, кастомные Toast-уведомления
└── README.md
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/cipo4kin/angel-demon.git
cd angel-demon
```

### 2. Установка зависимостей
Рекомендуется использовать виртуальное окружение:
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `backend/.env` на основе примера:
```env
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3
WEBAPP_URL=https://your-domain.duckdns.org
DB_PATH=backend/app/database/angel_demon.db
```

### 4. Запуск сервиса
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

После запуска:
- Документация Swagger API доступна по адресу: `http://localhost:8000/docs`
- Фронтенд Mini App доступен по корневому адресу: `http://localhost:8000/`

---

## 👨‍💻 Автор

- GitHub: [@cipo4kin](https://github.com/cipo4kin)
- Telegram Bot: [@angel_demon_ai_bot](https://t.me/angel_demon_ai_bot)
