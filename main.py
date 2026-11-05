import telebot
from telebot import types

from config import get_token
from database import init_db, save_user, save_profile, get_profile, get_user_count
from recommendations import CAREERS, recommend_career, get_career_text

TOKEN = get_token()
bot = telebot.TeleBot(TOKEN)
init_db()

# Ответы профориентационного диалога хранятся в памяти, профиль — в SQLite.
quiz_data = {}

def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🧭 Подобрать профессию", "💼 Профессии")
    keyboard.row("📚 Выучить что-то", "🧰 Развитие навыков")
    keyboard.row("👤 Мой профиль", "ℹ️ О проекте")
    return keyboard

def inline_links(items):
    keyboard = types.InlineKeyboardMarkup()
    for title, url in items:
        keyboard.add(types.InlineKeyboardButton(title, url=url))
    return keyboard

def show_career_list(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    for key, career in CAREERS.items():
        keyboard.add(types.InlineKeyboardButton(
            career["title"], callback_data=f"career:{key}"
        ))
    bot.send_message(chat_id, "Выбери профессию, о которой хочешь узнать:", reply_markup=keyboard)

def start_quiz(message):
    user_id = message.from_user.id
    quiz_data[user_id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("Выбираю профессию впервые", "Хочу сменить направление")
    keyboard.row("❌ Отмена")
    msg = bot.send_message(
        message.chat.id,
        "🧭 Давай подберём направление! Это не окончательный выбор профессии, "
        "а подсказка для знакомства с разными сферами.\n\n"
        "1/4. Ты выбираешь профессию впервые или хочешь сменить направление?",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(msg, quiz_stage)

def quiz_stage(message):
    if message.text == "❌ Отмена":
        return cancel_quiz(message)
    quiz_data[message.from_user.id]["stage"] = message.text
    msg = bot.send_message(
        message.chat.id,
        "2/4. Что тебе интересно? Напиши несколько вещей своими словами. "
        "Например: рисование, компьютеры, игры, техника, математика, помощь людям.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, quiz_interests)

def quiz_interests(message):
    if message.text == "❌ Отмена":
        return cancel_quiz(message)
    quiz_data[message.from_user.id]["interests"] = message.text.strip()[:1000]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("Создавать и придумывать", "Решать задачи и искать ошибки")
    keyboard.row("Общаться и помогать", "Работать с числами и информацией")
    keyboard.row("❌ Отмена")
    msg = bot.send_message(
        message.chat.id,
        "3/4. Какие занятия тебе ближе? Выбери вариант.",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(msg, quiz_tasks)

def quiz_tasks(message):
    if message.text == "❌ Отмена":
        return cancel_quiz(message)
    quiz_data[message.from_user.id]["preferred_tasks"] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row("Пока новичок", "Уже немного пробовал")
    keyboard.row("Есть небольшой опыт", "❌ Отмена")
    msg = bot.send_message(message.chat.id, "4/4. Какой у тебя сейчас опыт?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, quiz_finish)

def quiz_finish(message):
    user_id = message.from_user.id
    if message.text == "❌ Отмена":
        return cancel_quiz(message)
    data = quiz_data.pop(user_id, {})
    data["experience"] = message.text
    career_id = recommend_career(data.get("interests", ""), data.get("preferred_tasks", ""))
    save_profile(
        user_id,
        data.get("stage", ""),
        data.get("interests", ""),
        data.get("preferred_tasks", ""),
        data.get("experience", ""),
        career_id
    )
    career = CAREERS[career_id]
    text = (
        f"✨ Моя первая рекомендация: {career['title']}\n\n"
        f"Почему этот вариант может тебе подойти: {career['description']}\n\n"
        f"Это только предварительная рекомендация — попробуй мини-задание и посмотри, "
        f"нравится ли тебе сам процесс.\n\n"
        f"🎯 Твоё мини-задание:\n{career['task']}"
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Подробнее о профессии", callback_data=f"career:{career_id}"))
    keyboard.add(types.InlineKeyboardButton("Материалы для обучения", callback_data=f"learn:{career_id}"))
    bot.send_message(message.chat.id, text, reply_markup=keyboard)
    bot.send_message(message.chat.id, "Можешь продолжить изучение через меню 👇", reply_markup=main_menu())

def cancel_quiz(message):
    quiz_data.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Опрос отменён.", reply_markup=main_menu())

@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    bot.send_message(
        message.chat.id,
        "🤖 Привет! Я RoboCareer — помогу исследовать профессии, "
        "найти учебные материалы и попробовать небольшие задания.\n"
        "Нажми «Подобрать профессию», чтобы начать.",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "/start — главное меню\n"
        "/profile — показать профиль\n"
        "/quiz — начать профориентацию\n"
        "/cancel — отменить текущий опрос",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=["quiz"])
def quiz_command(message):
    start_quiz(message)

@bot.message_handler(commands=["profile"])
def profile_command(message):
    show_profile(message)

@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    cancel_quiz(message)

@bot.message_handler(commands=["stats"])
def stats_command(message):
    # В учебной версии статистика доступна только локальному владельцу проекта.
    bot.send_message(message.chat.id, f"👥 Пользователей в базе: {get_user_count()}")

@bot.message_handler(func=lambda m: m.text == "🧭 Подобрать профессию")
def quiz_button(message):
    start_quiz(message)

@bot.message_handler(func=lambda m: m.text == "💼 Профессии")
def professions_button(message):
    show_career_list(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "📚 Выучить что-то")
def learn_menu(message):
    keyboard = types.InlineKeyboardMarkup()
    for key, career in CAREERS.items():
        keyboard.add(types.InlineKeyboardButton(
            f"Учиться: {career['title']}", callback_data=f"learn:{key}"
        ))
    bot.send_message(message.chat.id, "Выбери направление — покажу учебные ресурсы:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "🧰 Развитие навыков")
def skills_menu(message):
    profile = get_profile(message.from_user.id)
    career_id = profile["recommended_career"] if profile else None
    if career_id in CAREERS:
        career = CAREERS[career_id]
        bot.send_message(
            message.chat.id,
            f"Для направления «{career['title']}» можно собрать небольшое портфолио. "
            "Начни с мини-задания из профориентации, затем сохрани результат и кратко опиши, "
            "что ты сделал и чему научился.",
            reply_markup=inline_links(career["portfolio"])
        )
    else:
        bot.send_message(message.chat.id, "Сначала пройди профориентацию — тогда я подберу ресурсы под твоё направление.")

@bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
def profile_button(message):
    show_profile(message)

def show_profile(message):
    profile = get_profile(message.from_user.id)
    if not profile:
        bot.send_message(message.chat.id, "Профиль пока пуст. Нажми «Подобрать профессию», чтобы заполнить его.", reply_markup=main_menu())
        return
    career = CAREERS.get(profile["recommended_career"], {})
    text = (
        "👤 Твой профиль\n\n"
        f"Выбор: {profile['stage']}\n"
        f"Интересы: {profile['interests']}\n"
        f"Предпочтения: {profile['preferred_tasks']}\n"
        f"Опыт: {profile['experience']}\n"
        f"Рекомендация: {career.get('title', 'Пока нет')}"
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Пройти опрос заново", callback_data="quiz:restart"))
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "🤖 RoboCareer — учебный проект для знакомства с профессиями. "
        "Он предлагает идеи и задания, но не принимает решение за тебя. "
        "Ссылки ведут на внешние образовательные ресурсы."
    )

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data or ""
    if data == "quiz:restart":
        bot.answer_callback_query(call.id)
        start_quiz(call.message)
        return
    if data.startswith("career:"):
        career_id = data.split(":", 1)[1]
        if career_id in CAREERS:
            bot.answer_callback_query(call.id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("📚 Где учиться?", callback_data=f"learn:{career_id}"))
            bot.send_message(call.message.chat.id, get_career_text(career_id), reply_markup=keyboard)
        return
    if data.startswith("learn:"):
        career_id = data.split(":", 1)[1]
        if career_id in CAREERS:
            bot.answer_callback_query(call.id)
            career = CAREERS[career_id]
            bot.send_message(
                call.message.chat.id,
                f"📚 Учебные материалы по направлению «{career['title']}»:",
                reply_markup=inline_links(career["learn"])
            )
        return
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: True, content_types=["text"])
def unknown(message):
    bot.send_message(
        message.chat.id,
        "Я пока не умею свободно отвечать на любые вопросы. "
        "Чтобы получить рекомендацию, нажми «🧭 Подобрать профессию».",
        reply_markup=main_menu()
    )

if __name__ == "__main__":
    print("RoboCareer запущен.")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
