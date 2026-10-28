# Развёртывание в Ubuntu / WSL2

## 1. Установка

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/besit-gh/habatica-tg-viewer.git habitica-companion
cd habitica-companion
cp .env.example .env
nano .env
chmod 600 .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Заполни `TELEGRAM_BOT_TOKEN`, `ALLOWED_TELEGRAM_USER_ID`, `HABITICA_USER_ID` и `HABITICA_API_TOKEN`. После проверки останови процесс через Ctrl+C. Не добавляй секреты в GitHub issues или коммиты.

## 2. systemd (необязательно)

В `/etc/wsl.conf` включи:

```ini
[boot]
systemd=true
```

В Windows PowerShell выполни `wsl --shutdown`, затем снова запусти Ubuntu. Для сервиса установи проект в `/opt/habitica-companion`, создай Linux-пользователя `habitica`, установи владельца каталога и `.env` в `habitica:habitica`, права `.env` — `600`. Скопируй `deploy/habitica-companion.service` в `/etc/systemd/system/`, затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now habitica-companion
sudo systemctl status habitica-companion
journalctl -u habitica-companion -f
```

Unit рассчитан на пути `/opt/habitica-companion` и отдельного пользователя `habitica`; исправь пути при другой установке. Не запускай бота от root. systemd перезапускает упавший процесс, но не запускает сам WSL2 после перезагрузки Windows.

## 3. Безопасное обновление

Перед обновлением убедись, что рабочее дерево чистое и активна ветка `main`:

```bash
cd ~/apps/habitica-companion
git status --short --branch
git pull --ff-only origin main
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/mypy app && .venv/bin/pytest -q && sudo systemctl restart habitica-companion
sudo systemctl --no-pager --full status habitica-companion
```

Если проверки падают, цепочка `&&` не перезапустит сервис. Для отката найди предыдущий рабочий коммит через `git log --oneline -5`, переключись на него, повтори проверки и перезапусти сервис. Изменения зависимостей нужно проверять отдельно: откат кода не исправит несовместимое окружение.

## 4. Безопасность и диагностика

- `.env` не коммитится; права файла — `600`.
- Токены не выводятся в логи.
- Для диагностики: `systemctl status habitica-companion` и `journalctl -u habitica-companion -n 100`.
- Бот не делает автоматических повторов. После тайм-аута мутации сначала обнови данные, так как результат операции может быть неоднозначным.
- API-клиент использует `X-Client` и 30-секундный интервал между запросами в соответствии с текущими правилами Habitica; последовательные действия могут быть медленными.
