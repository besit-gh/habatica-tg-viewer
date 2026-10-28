# Habitica Companion

Telegram-бот для управления своим Habitica из личного чата. Python 3.11+, aiogram 3.

## Что умеет

- Показывать профиль, характеристики, доступные данные инвентаря и квеста.
- Показывать привычки, ежедневные, разовые, награды и последние выполненные To-Do.
- Искать задачи по названию, фильтровать и листать список.
- Создавать задачу, менять её название, начислять выполнение и удалять после подтверждения.
- Отправлять карточку выбранной задачи в Telegram.
- Разрешать действия только Telegram ID из allowlist.

## Запуск для новичка (Ubuntu / WSL2)

1. Установи Python 3.11 или новее, Git и создай Telegram-бота через [@BotFather](https://t.me/BotFather). Сохрани выданный токен.
2. В настройках Habitica открой раздел API и скопируй **User ID** и **API Token**. Это разные значения.
3. Скопируй свой числовой Telegram ID из надёжного способа проверки собственного ID. Впиши его в `ALLOWED_TELEGRAM_USER_ID`.
4. Открой терминал Ubuntu/WSL2 и выполни команды:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/besit-gh/habatica-tg-viewer.git habitica-companion
cd habitica-companion
cp .env.example .env
nano .env
```

5. В `.env` замени демонстрационные значения на свои:

```dotenv
TELEGRAM_BOT_TOKEN=токен_от_BotFather
ALLOWED_TELEGRAM_USER_ID=твой_числовой_Telegram_ID
HABITICA_USER_ID=твой_Habitica_User_ID
HABITICA_API_TOKEN=твой_Habitica_API_Token
HABITICA_CLIENT_NAME=HabiticaCompanion
LOG_LEVEL=INFO
```

6. Сохрани файл в nano: **Ctrl+O**, Enter, затем **Ctrl+X**. Защити секреты и установи зависимости:

```bash
chmod 600 .env
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
ruff check .
mypy app
pytest -q
```

7. Если проверки завершились успешно, запусти бота:

```bash
python -m app.main
```

8. Открой созданного бота в Telegram и отправь `/start`. Затем пользуйся кнопками меню. Остановить процесс можно сочетанием **Ctrl+C**.

## Важные ограничения

- Не присылай токены в чат и никогда не коммить файл `.env`. В репозитории должен оставаться только `.env.example` с заглушками.
- Если ты не в allowlist, бот не выполнит команды.
- API-запросы Habitica намеренно разделены интервалом в 30 секунд для соблюдения опубликованных правил Habitica. Поэтому действия, требующие нескольких API-вызовов, могут занимать минуту и более.
- Автоматических повторов нет. Если операция завершилась тайм-аутом, сначала обнови список/проверь состояние в Habitica, а не нажимай повторно сразу.
- Успешный CI проверяет код с моками; он не подтверждает, что твои личные токены действительны. Первый `/start` проверит реальное подключение.
- Запуск в терминале работает, пока процесс и WSL2 запущены. Для фонового запуска смотри [инструкцию по WSL2 и systemd](docs/deployment.md).

## Разработка

```bash
pip install -r requirements-dev.txt
ruff check .
mypy app
pytest -q
```

GitHub Actions автоматически выполняет Ruff, mypy и pytest при push и pull request.

## Habitica API

Клиент передаёт обязательный `X-Client` и соблюдает официальные правила использования API: [API Usage Guidelines](https://github.com/HabitRPG/habitica/wiki/API-Usage-Guidelines).
