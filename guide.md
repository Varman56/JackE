# Гайд по развертыванию проекта JackE

## Первоначальная настройка

### 1. Установка uv

Если у вас еще не установлен `uv`, установите его:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Или через pip:**
```bash
pip install uv
```

### 2. Создание виртуального окружения и установка зависимостей

```bash
uv sync
```

### 3. Активация виртуального окружения

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

Или используйте `uv run` для запуска команд без явной активации окружения.

## Разработка

### Запуск VM

```bash
uv run python vm/main.py
```

### workflow перед коммитом

Запускайте эти команды перед каждым коммитом:

```bash
# 1. Форматирование кода
uv run ruff format .

# 2. Исправление проблем линтера
uv run ruff check --fix .

# 3. Проверка типов
uv run mypy vm/ cmplr/

# 4. Если все ОК, коммитим
git add .
git commit -m "your commit message"

# скоро еще тесты добавим...
```

### Альтернатива: все в одной строке

```bash
ruff format . && uv run ruff check --fix . && mypy vm/ cmplr/ && echo "✅ All checks passed!"
```

## Добавление новых зависимостей

```bash
uv add package-name
```

## Troubleshooting

### Проблемы с версией Python
Если требуется Python 3.14, но у вас другая версия:
```bash
uv python install 3.14
uv python pin 3.14
```

### Сброс окружения
```bash
rm -rf .venv
uv sync
```
