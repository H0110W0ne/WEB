# Странник — лабораторная работа №7 (Docker + микросервисы + CI/CD)

- регистрация пользователя и хеширование пароля;
- WebSocket-комментарии в реальном времени;
- отправка уведомлений в Telegram;
- контейнеризация и локальное развёртывание через Docker Compose;
- CI/CD через GitHub Actions.

## Архитектура микросервисов
- **web** — Django + Channels + WebSocket + HTML/API.
- **worker** — Celery-воркер, который асинхронно отправляет уведомления в Telegram.
- **db** — PostgreSQL.
- **redis** — брокер Celery и channel layer для Channels.
- **nginx** — reverse proxy, отдача статики и проксирование WebSocket.

## Ключевые файлы
- `Dockerfile` — образ Python-сервисов.
- `compose.yaml` — локальное развёртывание всех сервисов.
- `docker/nginx/default.conf` — reverse proxy и WebSocket proxy.
- `.github/workflows/ci-cd.yml` — CI/CD pipeline.
- `strannik_site/celery.py` — конфигурация Celery.
- `main/tasks.py` — асинхронная отправка в Telegram.
