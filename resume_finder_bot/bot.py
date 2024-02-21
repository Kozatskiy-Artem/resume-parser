import os

from dotenv import load_dotenv
from pydantic import ValidationError
from telebot import TeleBot, types

from resume_parser.dto import CriteriaDTO
from resume_parser.exceptions import ResumeNotFoundError
from resume_parser.robota_ua_resume_parser import RobotaUaResumeParser
from resume_parser.robota_ua_resume_searcher import RobotaUaResumeSearcher
from resume_parser.work_ua_resume_parser import WorkUaResumeParser
from resume_parser.work_ua_resume_searcher import SALARY, WorkUaResumeSearcher

load_dotenv()
TOKEN = os.environ.get("TOKEN")

bot = TeleBot(TOKEN, parse_mode="HTML")

user_responses = {}


@bot.message_handler(commands=["start"])
def start(message):
    user_responses[message.chat.id] = {}
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    position = types.KeyboardButton(text="Посада")
    location = types.KeyboardButton(text="Локація")
    salary_from = types.KeyboardButton(text="Досвід")
    salary_to = types.KeyboardButton(text="Зарплата від")
    experience = types.KeyboardButton(text="Зарплата до")
    keywords = types.KeyboardButton(text="Ключові слова")
    keyboard.add(position, location, salary_from, salary_to, experience, keywords)
    bot.send_message(
        message.chat.id,
        """
<b>Вас вітає бот ResumeFinder🔍</b>

Я допоможу Вам знайти кандидатів з <b>релевантними резюме</b> на таких платформах, як work.ua та robota.ua. 
Використовуйте кнопки розміщенні на клавіатурі👇 для того, щоб вказати параметри пошуку🔍. 
<b>Обов'язково</b> вкажіть посаду кандидата. Також вкажіть інші параметри, що допоможуть звузити коло пошуку. 
Вказані ключові слова допоможуть оцінити релевантність резюме кандидата.

/help - щоб дізнатись усі доступні команди.
        """,
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["help"])
def help_handler(message):
    bot.send_message(
        message.chat.id,
        """
<b>Доступні команди</b>

/start - Команда щоб розпочати роботу з ботом.
/help - Команда щоб відобразити список усіх доступних команд та їх короткий опис.
/check - Команда щоб вивести задані параметри для пошуку резюме.
/clear - Команда щоб очистити задані параметри.
/find_on_work - Команда щоб виконати пошук релевантних резюме за попередньо заданими параметрами на сайті work.ua.
/find_on_robota - Команда щоб виконати пошук релевантних резюме за попередньо заданими параметрами на сайті robota.ua.
/find_on_all - Команда щоб виконати пошук релевантних резюме за попередньо заданими параметрами на обох платформах.

Перед пошуком резюме <b>обов'язково введіть параметри</b> для пошуку. 
Для цього використайте спеціальні кнопки на клавіатурі або напишіть вручну, наприклад, <i>Посада</i>,
що буде сигналізувати про те, що Ви хочете вказати даний параметр.

<b>Вказуйте ключові слова та навички</b>, чим більше тим краще, це дозволить виділити найбільш релевантні резюме.
        """,
    )


@bot.message_handler(commands=["find_on_work"])
def find_resume_on_work(message):
    try:
        user_responses[message.chat.id]
    except KeyError:
        bot.send_message(message.chat.id, "Спочатку виконайте команду /start")
        return

    try:
        criteria = get_criteria(message)
    except ValidationError:
        bot.send_message(message.chat.id, "Посада кандидата не вказана або введені некоректні дані в інших параметрах")
        return

    bot.send_message(message.chat.id, "Шукаємо кандидатів на work.ua, це може зайняти певний час.")

    work_ua_searcher = WorkUaResumeSearcher()

    try:
        work_ua_searcher.set_params(criteria)
    except ResumeNotFoundError:
        bot.send_message(message.chat.id, "Резюме кандидатів за заданими параметрами не знайдено!")
        return

    work_ua_resume_parser = WorkUaResumeParser()
    work_ua_resume_parser.pars_resumes(work_ua_searcher.resume_links, criteria)

    work_ua_results = work_ua_resume_parser.get_relevant_resumes(5)
    bot.send_message(message.chat.id, "<b>Звіт пошуку кандидатів на work.ua</b>")
    for index, result in enumerate(work_ua_results.items()):
        if result[1]["is_file"]:
            bot.send_message(
                message.chat.id,
                f"""
📌 Кандидат №{index + 1}
- <b>Посада</b>: <a href="{result[0]}">{result[1]["position"]}</a>
- Усі ключові слова з якими знайдено співпадіння в резюме: {result[1]["matching_keywords"]}
- Кількість балів: {result[1]["points"]}
- Резюме завантажено файлом, а не заповнено на сайті, тому розділи навичок, освіти та досвіду не знайдені.
                """
            )
        else:
            bot.send_message(
                message.chat.id,
                f"""
📌 Кандидат №{index + 1}
- <b>Посада</b>: <a href="{result[0]}">{result[1]["position"]}</a>
- {result[1]["experience"]}
- {result[1]["education"]}
- Навички кандидата, що співпали з вказаними: {result[1]["matching_skills"]}
- Усі ключові слова з якими знайдено співпадіння в резюме: {result[1]["matching_keywords"]}
- Кількість балів: {result[1]["points"]}
                """
            )


@bot.message_handler(commands=["find_on_robota"])
def find_resume_on_robota(message):
    try:
        user_responses[message.chat.id]
    except KeyError:
        bot.send_message(message.chat.id, "Спочатку виконайте команду /start")
        return

    try:
        criteria = get_criteria(message)
    except ValidationError:
        bot.send_message(message.chat.id, "Посада кандидата не вказана або введені некоректні дані в інших параметрах")
        return

    bot.send_message(message.chat.id, "Шукаємо кандидатів на robota.ua, це може зайняти певний час.")

    robota_ua_searcher = RobotaUaResumeSearcher()

    try:
        robota_ua_searcher.set_params(criteria)
    except ResumeNotFoundError:
        bot.send_message(message.chat.id, "Резюме кандидатів за заданими параметрами не знайдено!")
        return

    robota_ua_resume_parser = RobotaUaResumeParser()
    robota_ua_resume_parser.pars_resumes(robota_ua_searcher.resume_links, criteria)

    robota_ua_results = robota_ua_resume_parser.get_relevant_resumes(5)
    bot.send_message(message.chat.id, "<b>Звіт пошуку кандидатів на robota.ua</b>")
    for index, result in enumerate(robota_ua_results.items()):
        bot.send_message(
            message.chat.id,
            f"""
📌 Кандидат №{index + 1}
- <b>Посада</b>: <a href="{result[0]}">{result[1]["position"]}</a>
- {result[1]["experience"]}
- {result[1]["education"]}
- Усі ключові слова з якими знайдено співпадіння в резюме: {result[1]["matching_keywords"]}
- Кількість балів: {result[1]["points"]}
            """
        )


@bot.message_handler(commands=["find_on_all"])
def find_resume_on_all(message):
    find_resume_on_work(message)
    find_resume_on_robota(message)


@bot.message_handler(commands=["check"])
def check_params(message):
    try:
        user_responses[message.chat.id]
    except KeyError:
        bot.send_message(message.chat.id, "Спочатку виконайте команду /start")
        return

    bot.send_message(
        message.chat.id,
        f"""
<b>Параметри пошуку резюме</b>: 
Позиція: <i>{user_responses[message.chat.id].get('position', 'Не вказана')}</i>
Локація: <i>{user_responses[message.chat.id].get('location', 'Не вказана')}</i>
Досвід: <i>{user_responses[message.chat.id].get('experience', 'Не вказаний')}</i>
Зарплата (від): <i>{user_responses[message.chat.id].get('salary_from', 'Не вказана')}</i>
Зарплата (до): <i>{user_responses[message.chat.id].get('salary_to', 'Не вказана')}</i>
Ключові слова: <i>{user_responses[message.chat.id].get('keywords', 'Не вказані')}</i>
"""
    )


@bot.message_handler(commands=["clear"])
def clear_params(message):
    try:
        user_responses[message.chat.id]
    except KeyError:
        bot.send_message(message.chat.id, "Спочатку виконайте команду /start")
        return

    user_responses[message.chat.id] = {}
    bot.send_message(message.chat.id, "Параметри очищено")


def get_criteria(message):
    criteria = CriteriaDTO(
        position=user_responses[message.chat.id].get("position"),
        location=user_responses[message.chat.id].get("location"),
        salary_from=user_responses[message.chat.id].get("salary_from"),
        salary_to=user_responses[message.chat.id].get("salary_to"),
        experience=user_responses[message.chat.id].get("experience"),
        skills_and_keywords=user_responses[message.chat.id].get("keywords"),
    )
    return criteria


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    try:
        user_responses[message.chat.id]
    except KeyError:
        bot.send_message(message.chat.id, "Спочатку виконайте команду /start")
        return

    if message.text.lower() == "посада":
        bot.send_message(message.chat.id, "Введіть назву посади на яку Ви шукаєте кандидата")
        bot.register_next_step_handler(message, set_position)
    if message.text.lower() == "локація":
        bot.send_message(message.chat.id, "Введіть назву міста")
        bot.register_next_step_handler(message, set_location)
    if message.text.lower() == "зарплата від":
        bot.send_message(
            message.chat.id,
            "Введіть мінімальне значення очікуваної зарплати кандидата в грн. "
            f"Доступні значення: {list(SALARY.keys())[1:]}",
        )
        bot.register_next_step_handler(message, set_salary_from)
    if message.text.lower() == "зарплата до":
        bot.send_message(
            message.chat.id,
            "Введіть максимальне значення очікуваної зарплати кандидата в грн. "
            f"Доступні значення: {list(SALARY.keys())[1:]}",
        )
        bot.register_next_step_handler(message, set_salary_to)
    if message.text.lower() == "досвід":
        bot.send_message(message.chat.id, "Введіть досвід кандидата у роках")
        bot.register_next_step_handler(message, set_experience)
    if message.text.lower() == "ключові слова":
        bot.send_message(
            message.chat.id, "Введіть необхідні навички кандидата та ключові слова в резюме, перелік через кому"
        )
        bot.register_next_step_handler(message, set_keywords)


def set_position(message):
    user_responses[message.chat.id]["position"] = message.text
    bot.send_message(message.chat.id, f"Посада кандидата: {message.text}")


def set_location(message):
    user_responses[message.chat.id]["location"] = message.text
    bot.send_message(message.chat.id, f"Місто пошуку: {message.text}")


def set_salary_from(message):
    user_responses[message.chat.id]["salary_from"] = message.text
    bot.send_message(message.chat.id, f"Зарплатні очікування (від): {message.text}")


def set_salary_to(message):
    user_responses[message.chat.id]["salary_to"] = message.text
    bot.send_message(message.chat.id, f"Зарплатні очікування (до): {message.text}")


def set_experience(message):
    user_responses[message.chat.id]["experience"] = message.text
    bot.send_message(message.chat.id, f"Досвід роботи кандидата: {message.text}")


def set_keywords(message):
    user_responses[message.chat.id]["keywords"] = message.text.split(", ")
    bot.send_message(message.chat.id, f"Навички кандидата та ключові слова в резюме: {message.text}")


def run_bot():
    bot.infinity_polling()
