import os
from html import escape

import requests

from .models import Registration


def build_registration_text(registration: Registration) -> str:
    comment = registration.message.strip() or 'Не указан'
    return (
        '<b>Новая регистрация пользователя</b>\n'
        f'<b>Логин:</b> {escape(registration.user.username)}\n'
        f'<b>Имя:</b> {escape(registration.first_name)}\n'
        f'<b>Фамилия:</b> {escape(registration.last_name)}\n'
        f'<b>Email:</b> {escape(registration.email)}\n'
        f'<b>Телефон:</b> {escape(registration.phone)}\n'
        f'<b>Возраст:</b> {registration.age}\n'
        f'<b>Направление:</b> {escape(registration.direction.name)}\n'
        f'<b>Комментарий:</b> {escape(comment)}'
    )


def send_telegram_message(text: str) -> dict:
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token:
        raise RuntimeError('Не задана переменная окружения TELEGRAM_BOT_TOKEN')
    if not chat_id:
        raise RuntimeError('Не задана переменная окружения TELEGRAM_CHAT_ID')

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }

    response = requests.post(url, json=payload, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f'Telegram API вернул ошибку {response.status_code}: {response.text}')

    data = response.json()

    if not data.get('ok'):
        raise RuntimeError(f'Ошибка Telegram API: {data}')

    return data
