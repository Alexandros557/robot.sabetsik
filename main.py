
from pathlib import Path

import telebot
from telebot import types

from config import TOKEN
from database import init_db, save_user, get_user_count


# ==========================================
# НАСТРОЙКИ
# ==========================================

if not TOKEN:
    raise RuntimeError(
        "Не найден токен! Задай TELEGRAM_BOT_TOKEN."
    )

bot = telebot.TeleBot(TOKEN)

BASE_DIR = Path(__file__).parent
MATERIALS_DIR = BASE_DIR / "materials"

init_db()


# ==========================================
# ПРОФЕССИИ И УЧЕБНЫЕ МАТЕРИАЛЫ
# ==========================================

CAREERS = {
    "python": {
        "title": "💻 Python-разработчик",
        "description": "Создаёт программы, Telegram-ботов и приложения.",
        "pros": "Python применяется в автоматизации, веб-разработке и анализе данных.",
        "cons": "Нужно развивать логику, практиковаться и исправлять ошибки.",
        "links": [
            ("📖 Учебник Python", "https://docs.python.org/3/tutorial/"),
            ("🎓 Практика Python", "https://www.kaggle.com/learn/intro-to-programming"),
            ("🎬 Видео Python", "https://www.youtube.com/results?search_query=Python+для+начинающих")
        ]
    },

    "games": {
        "title": "🎮 Разработчик игр",
        "description": "Создаёт игровые механики, уровни, персонажей и интерфейсы.",
        "pros": "Можно придумывать и создавать собственные игры.",
        "cons": "Большие проекты требуют времени и командной работы.",
        "links": [
            ("📖 Первый проект Godot", "https://docs.godotengine.org/en/latest/getting_started/first_2d_game/index.html"),
            ("🎓 Обучение Godot", "https://godotengine.org/"),
            ("🎬 Видео по созданию игр", "https://www.youtube.com/results?search_query=Godot+для+начинающих")
        ]
    },

    "qa": {
        "title": "🧪 Тестировщик ПО",
        "description": "Проверяет программы, находит ошибки и описывает их.",
        "pros": "Можно начинать с ручного тестирования и простых проектов.",
        "cons": "Нужно внимательно проверять множество сценариев.",
        "links": [
            ("📖 Основы тестирования", "https://www.istqb.org/"),
            ("🎓 Практика тестирования", "https://www.ministryoftesting.com/"),
            ("🎬 Видео по тестированию", "https://www.youtube.com/results?search_query=тестирование+ПО+для+начинающих")
        ]
    },

    "web": {
        "title": "🌐 Веб-разработчик",
        "description": "Создаёт сайты и веб-приложения.",
        "pros": "Можно быстро увидеть результат в браузере.",
        "cons": "Нужно изучать HTML, CSS и JavaScript.",
        "links": [
            ("📖 Учебник MDN", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
            ("🎓 Курсы freeCodeCamp", "https://www.freecodecamp.org/learn/"),
            ("🎬 Видео по веб-разработке", "https://www.youtube.com/results?search_query=HTML+CSS+JavaScript+для+начинающих")
        ]
    },

    "design": {
        "title": "🎨 UI/UX-дизайнер",
        "description": "Проектирует внешний вид сайтов и удобство приложений.",
        "pros": "Можно сочетать творчество, дизайн и технологии.",
        "cons": "Нужно изучать композицию, интерфейсы и потребности пользователей.",
        "links": [
            ("📖 Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613-Learn-design"),
            ("🎓 Основы веб-дизайна", "https://www.interaction-design.org/"),
            ("🎬 Видео по UI/UX", "https://www.youtube.com/results?search_query=UI+UX+дизайн+для+начинающих")
        ]
    },

    "data": {
        "title": "📊 Аналитик данных",
        "description": "Изучает данные, таблицы и ищет закономерности.",
        "pros": "Помогает находить полезные выводы из информации.",
        "cons": "Нужно изучать математику, таблицы и инструменты анализа.",
        "links": [
            ("📖 Kaggle Learn", "https://www.kaggle.com/learn/"),
            ("🎓 Основы SQL", "https://sqlbolt.com/"),
            ("🎬 Видео по анализу данных", "https://www.youtube.com/results?search_query=анализ+данных+для+начинающих")
        ]
    }
}


# ==========================================
# ГЛАВНОЕ МЕНЮ
# ==========================================

def create_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🤖 О проекте",
        "💼 Профессии"
    )

    keyboard.row(
        "📚 Выучить что-то",
        "💼 Работа"
    )

    keyboard.row(
        "👤 Мой профиль"
    )

    return keyboard


# ==========================================
# СТАРТ
# ==========================================

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
        "💼 Знакомься с профессиями.\n"
        "📚 Изучай новые навыки.\n"
        "🎬 Находи учебные видео.\n"
        "📄 Получай учебные файлы.\n"
        "🔎 Открывай полезные ресурсы.\n\n"
        "Выбери раздел ниже 👇",
        reply_markup=create_menu()
    )


# ==========================================
# ПОМОЩЬ И СТАТИСТИКА
# ==========================================

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "/start — главное меню\n"
        "/help — помощь\n"
        "/stats — количество пользователей"
    )


@bot.message_handler(commands=["stats"])
def stats(message):
    bot.send_message(
        message.chat.id,
        f"📊 Пользователей в базе: {get_user_count()}"
    )


# ==========================================
# О ПРОЕКТЕ
# ==========================================

@bot.message_handler(
    func=lambda m: m.text == "🤖 О проекте"
)
def about(message):
    bot.send_message(
        message.chat.id,
        "🤖 RoboCareer — помощник по выбору профессии!\n\n"
        "🎯 Цель проекта — помочь изучить разные профессии.\n\n"
        "📚 В боте есть учебные материалы.\n"
        "💼 Есть информация о направлениях работы.\n"
        "🧠 Можно изучать навыки и новые технологии."
    )


# ==========================================
# СПИСОК ПРОФЕССИЙ
# ==========================================

@bot.message_handler(
    func=lambda m: m.text == "💼 Профессии"
)
def careers(message):
    keyboard = types.InlineKeyboardMarkup()

    for career_id, career in CAREERS.items():
        keyboard.add(
            types.InlineKeyboardButton(
                career["title"],
                callback_data=f"career_{career_id}"
            )
        )

    bot.send_message(
        message.chat.id,
        "💼 Выбери интересную профессию:",
        reply_markup=keyboard
    )


# ==========================================
# ИНФОРМАЦИЯ О ПРОФЕССИИ
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("career_")
)
def career_details(call):
    career_id = call.data.removeprefix("career_")
    career = CAREERS.get(career_id)

    bot.answer_callback_query(call.id)

    if not career:
        bot.send_message(
            call.message.chat.id,
            "Профессия не найдена."
        )
        return

    text = (
        f"{career['title']}\n\n"
        f"📌 Чем занимается:\n"
        f"{career['description']}\n\n"
        f"✅ Плюсы:\n"
        f"{career['pros']}\n\n"
        f"⚠️ Сложности:\n"
        f"{career['cons']}"
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "📚 Где учиться?",
            callback_data=f"study_{career_id}"
        )
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=keyboard
    )


# ==========================================
# ССЫЛКИ ДЛЯ ОБУЧЕНИЯ ПО ПРОФЕССИИ
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("study_")
)
def study_career(call):
    career_id = call.data.removeprefix("study_")
    career = CAREERS.get(career_id)

    bot.answer_callback_query(call.id)

    if not career:
        bot.send_message(
            call.message.chat.id,
            "Учебные материалы не найдены."
        )
        return

    keyboard = types.InlineKeyboardMarkup()

    for title, url in career["links"]:
        keyboard.add(
            types.InlineKeyboardButton(
                title,
                url=url
            )
        )

    bot.send_message(
        call.message.chat.id,
        f"📚 Материалы для профессии:\n"
        f"{career['title']}\n\n"
        "Выбери учебник, практику или видео 👇",
        reply_markup=keyboard
    )


# ==========================================
# ОБЩЕЕ ОБУЧЕНИЕ
# ==========================================

@bot.message_handler(
    func=lambda m: m.text == "📚 Выучить что-то"
)
def learning(message):
    keyboard = types.InlineKeyboardMarkup()

    for career_id, career in CAREERS.items():
        keyboard.add(
            types.InlineKeyboardButton(
                career["title"],
                callback_data=f"study_{career_id}"
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "📄 Получить PDF",
            callback_data="learn_pdf"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🎬 Получить видео",
            callback_data="learn_video"
        )
    )

    bot.send_message(
        message.chat.id,
        "📚 Что хочешь изучить?\n\n"
        "Выбери профессию или учебный файл:",
        reply_markup=keyboard
    )


# ==========================================
# ОТПРАВКА PDF И ВИДЕО
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data in [
        "learn_pdf",
        "learn_video"
    ]
)
def send_material(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id

    if call.data == "learn_pdf":
        file_path = MATERIALS_DIR / "python_guide.pdf"

        if file_path.is_file():
            try:
                with file_path.open("rb") as file:
                    bot.send_document(
                        chat_id,
                        file,
                        caption="📄 Учебное пособие Python"
                    )
            except Exception as error:
                print("Ошибка отправки PDF:", error)
                bot.send_message(
                    chat_id,
                    "Не удалось отправить PDF."
                )
        else:
            bot.send_message(
                chat_id,
                "📄 Файл пока не добавлен.\n\n"
                "Положи python_guide.pdf "
                "в папку materials."
            )

    elif call.data == "learn_video":
        file_path = MATERIALS_DIR / "python_lesson.mp4"

        if file_path.is_file():
            try:
                with file_path.open("rb") as file:
                    bot.send_video(
                        chat_id,
                        file,
                        caption="🎬 Учебное видео Python"
                    )
            except Exception as error:
                print("Ошибка отправки видео:", error)
                bot.send_message(
                    chat_id,
                    "Не удалось отправить видео."
                )
        else:
            keyboard = types.InlineKeyboardMarkup()

            keyboard.add(
                types.InlineKeyboardButton(
                    "▶️ Видео Python",
                    url="https://www.youtube.com/results?search_query=Python+для+начинающих"
                )
            )

            bot.send_message(
                chat_id,
                "🎬 Видео пока не добавлено.\n"
                "Можешь найти уроки по ссылке:",
                reply_markup=keyboard
            )


# ==========================================
# РАЗДЕЛ РАБОТА
# ==========================================

@bot.message_handler(
    func=lambda m: m.text == "💼 Работа"
)
def work(message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "💻 IT и программирование",
            callback_data="work_it"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🎨 Дизайн",
            callback_data="work_design"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📊 Аналитика",
            callback_data="work_data"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔎 Изучить вакансии",
            url="https://www.linkedin.com/jobs/"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🧰 Практика GitHub",
            url="https://github.com/skills"
        )
    )

    bot.send_message(
        message.chat.id,
        "💼 Раздел «Работа»\n\n"
        "Выбери направление, чтобы узнать, "
        "какие навыки стоит изучать.\n\n"
        "Также можно посмотреть требования "
        "к профессиям и учебные проекты 👇",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("work_")
)
def work_direction(call):
    directions = {
        "work_it": (
            "💻 IT и программирование\n\n"
            "Полезные навыки:\n"
            "• Python\n"
            "• HTML и CSS\n"
            "• JavaScript\n"
            "• Git и GitHub\n\n"
            "Начни с небольших проектов."
        ),
        "work_design": (
            "🎨 Дизайн\n\n"
            "Полезные навыки:\n"
            "• Figma\n"
            "• Композиция\n"
            "• Цвет и типографика\n"
            "• Проектирование интерфейсов"
        ),
        "work_data": (
            "📊 Аналитика данных\n\n"
            "Полезные навыки:\n"
            "• Python\n"
            "• SQL\n"
            "• Таблицы\n"
            "• Основы статистики"
        )
    }

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        directions.get(
            call.data,
            "Информация пока недоступна."
        )
    )


# ==========================================
# ПРОФИЛЬ
# ==========================================

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
        "В будущем здесь появятся "
        "твои интересы и навыки."
    )


# ==========================================
# НЕИЗВЕСТНЫЕ СООБЩЕНИЯ
# ==========================================

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


# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == "__main__":
    print("🤖 RoboCareer запущен!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
