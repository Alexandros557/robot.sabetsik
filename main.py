
from pathlib import Path

import telebot
from telebot import types

from config import TOKEN
from database import init_db, save_user, get_user_count
from recommendations import get_career_text


# ---------- НАСТРОЙКИ ----------

if not TOKEN:
    raise RuntimeError(
        "Не найден токен! Сначала задай переменную "
        "окружения TELEGRAM_BOT_TOKEN."
    )

bot = telebot.TeleBot(TOKEN)

BASE_DIR = Path(__file__).parent
MATERIALS_DIR = BASE_DIR / "materials"


# ---------- БАЗА ДАННЫХ ----------

init_db()


# ---------- ГЛАВНОЕ МЕНЮ ----------

def create_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        types.KeyboardButton("🤖 О проекте"),
        types.KeyboardButton("💼 Профессии")
    )

    keyboard.row(
        types.KeyboardButton("📚 Выучить что-то"),
        types.KeyboardButton("💼 Работа")
    )

    keyboard.row(
        types.KeyboardButton("👤 Мой профиль")
    )

    return keyboard


# ---------- СТАРТ ----------

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user

    save_user(
        user.id,
        user.username,
        user.first_name
    )

    name = user.first_name or "друг"

    bot.send_message(
        message.chat.id,
        f"Привет, {name}! 👋\n\n"
        "Я RoboCareer — твой помощник "
        "в мире профессий! 🤖\n\n"
        "Здесь ты сможешь:\n"
        "💼 Знакомиться с профессиями\n"
        "📚 Изучать программирование\n"
        "🎬 Смотреть учебные видео\n"
        "📄 Получать учебные файлы\n"
        "🔎 Находить полезные ресурсы\n\n"
        "Выбери нужный раздел в меню 👇",
        reply_markup=create_menu()
    )


# ---------- ПОМОЩЬ ----------

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "🤖 RoboCareer — помощь\n\n"
        "/start — главное меню\n"
        "/help — список команд\n"
        "/stats — количество пользователей"
    )


# ---------- СТАТИСТИКА ----------

@bot.message_handler(commands=["stats"])
def stats(message):
    bot.send_message(
        message.chat.id,
        f"📊 Пользователей в базе: {get_user_count()}"
    )


# ---------- О ПРОЕКТЕ ----------

@bot.message_handler(
    func=lambda m: m.text == "🤖 О проекте"
)
def about(message):
    bot.send_message(
        message.chat.id,
        "🤖 RoboCareer — помощник по выбору профессии!\n\n"
        "🎯 Цель — помочь изучить разные профессии.\n\n"
        "🧠 В дальнейшем бот сможет учитывать "
        "твои интересы, навыки и опыт.\n\n"
        "📚 Он будет предлагать обучение, "
        "полезные ссылки и карьерные советы."
    )


# ---------- ПРОФЕССИИ ----------

@bot.message_handler(
    func=lambda m: m.text == "💼 Профессии"
)
def careers(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "💻 Python-разработчик",
            callback_data="career_python"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🎮 Разработчик игр",
            callback_data="career_games"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🧪 Тестировщик ПО",
            callback_data="career_qa"
        )
    )

    bot.send_message(
        message.chat.id,
        "💼 Выбери профессию:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("career_")
)
def career_details(call):
    career_id = call.data.removeprefix("career_")

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        get_career_text(career_id)
    )


# ---------- ОБУЧЕНИЕ ----------

@bot.message_handler(
    func=lambda m: m.text == "📚 Выучить что-то"
)
def learning(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🐍 Изучить Python",
            callback_data="learn_python"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🎮 Создание игр",
            callback_data="learn_games"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🎬 Учебное видео",
            callback_data="learn_video"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📄 Учебный PDF",
            callback_data="learn_pdf"
        )
    )

    bot.send_message(
        message.chat.id,
        "📚 Чему хочешь научиться?\n"
        "Выбери один из вариантов 👇",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("learn_")
)
def learning_material(call):
    chat_id = call.message.chat.id
    action = call.data

    bot.answer_callback_query(call.id)

    if action == "learn_python":
        bot.send_message(
            chat_id,
            "🐍 Изучай Python с официального учебника:\n\n"
            "https://docs.python.org/3/tutorial/\n\n"
            "Совет: начни с переменных, условий "
            "и циклов."
        )

    elif action == "learn_games":
        bot.send_message(
            chat_id,
            "🎮 Попробуй создать свою первую игру!\n\n"
            "Официальная документация Godot:\n"
            "https://docs.godotengine.org/en/stable/\n\n"
            "Начни с простого 2D-проекта."
        )

    elif action == "learn_video":
        video = MATERIALS_DIR / "python_lesson.mp4"

        if video.is_file():
            with video.open("rb") as file:
                bot.send_video(
                    chat_id,
                    file,
                    caption="🎬 Учебный урок Python"
                )
        else:
            keyboard = types.InlineKeyboardMarkup()

            keyboard.add(
                types.InlineKeyboardButton(
                    "▶️ Найти уроки на YouTube",
                    url=(
                        "https://www.youtube.com/results"
                        "?search_query=Python+для+начинающих"
                    )
                )
            )

            bot.send_message(
                chat_id,
                "🎬 Учебное видео пока не добавлено.\n"
                "Пока можешь выбрать урок по ссылке:",
                reply_markup=keyboard
            )

    elif action == "learn_pdf":
        pdf = MATERIALS_DIR / "python_guide.pdf"

        if pdf.is_file():
            with pdf.open("rb") as file:
                bot.send_document(
                    chat_id,
                    file,
                    caption="📄 Учебное пособие Python"
                )
        else:
            bot.send_message(
                chat_id,
                "📄 PDF пока не добавлен.\n\n"
                "Добавь файл python_guide.pdf "
                "в папку materials."
            )


# ---------- РАБОТА ----------

@bot.message_handler(
    func=lambda m: m.text == "💼 Работа"
)
def work(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🔎 Вакансии на LinkedIn",
            url="https://www.linkedin.com/jobs/"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🧰 Практика на GitHub",
            url="https://github.com/skills"
        )
    )

    bot.send_message(
        message.chat.id,
        "💼 Раздел «Работа»\n\n"
        "Чтобы подготовиться к будущей профессии:\n\n"
        "✅ Создавай учебные проекты.\n"
        "✅ Собирай портфолио.\n"
        "✅ Учись пользоваться GitHub.\n"
        "✅ Изучай требования к вакансиям.\n\n"
        "Полезные ссылки находятся ниже 👇",
        reply_markup=keyboard
    )


# ---------- ПРОФИЛЬ ----------

@bot.message_handler(
    func=lambda m: m.text == "👤 Мой профиль"
)
def profile(message):
    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "не указан"
    )

    bot.send_message(
        message.chat.id,
        "👤 Твой профиль RoboCareer\n\n"
        f"Имя: {user.first_name or 'не указано'}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n\n"
        "Персональные рекомендации появятся "
        "в следующей версии."
    )


# ---------- НЕИЗВЕСТНЫЕ СООБЩЕНИЯ ----------

@bot.message_handler(
    content_types=["text"],
    func=lambda m: True
)
def unknown(message):
    bot.send_message(
        message.chat.id,
        "🤔 Я пока не понимаю эту команду.\n\n"
        "Выбери кнопку в меню или отправь /start.",
        reply_markup=create_menu()
    )


# ---------- ЗАПУСК ----------

if __name__ == "__main__":
    print("🤖 RoboCareer запущен!")
    bot.infinity_polling()
