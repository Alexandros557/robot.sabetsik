import os

def get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8971462848:AAEaguwPAz_UvSLLUXGA1PwHJjUtBTK54w4").strip()
    if not token:
        raise RuntimeError(
            "Не задан токен Telegram-бота. "
            "Создайте переменную окружения TELEGRAM_BOT_TOKEN и перезапустите бота. "
            "Не вставляйте токен в код и не публикуйте его."
        )
    if ":" not in token:
        raise RuntimeError(
            "Переменная TELEGRAM_BOT_TOKEN задана, но токен выглядит неверно: "
            "в нём должен присутствовать символ ':'. Проверьте значение в BotFather."
        )
    return token
