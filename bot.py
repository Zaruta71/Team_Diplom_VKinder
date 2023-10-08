# Сценарий с логикой бота для поиска кандидатов на романтические свидания

# Импортирование функции sleep из модуля time
from time import sleep

from config import GROUP_TOKEN
# Импортирование необходимых компонентов из библиотеки vkbottle
from vkbottle import API, Keyboard, EMPTY_KEYBOARD, Text, KeyboardButtonColor, CtxStorage
from vkbottle.bot import Message, Bot

# Импортирование пользовательских модулей и компонентов
import db_interaction
from maintenance import _make_user, _candidate_search, _make_candidate, _get_photos, _make_photo, _get_top3_photo
from models import User

# Создание экземпляра API с использованием токена группы
api = API(GROUP_TOKEN)

# Создание экземпляра Bot с использованием API
bot = Bot(api=api)

# Создание хранилища контекста
ctx_storage = CtxStorage()


# Определение обработчика для команды "start" или текста "/start"
@bot.on.message(payload={"command": "start"})
@bot.on.message(text="/start")
async def start_handler(message: Message):
    ''' Обработчик-функция для приветствия пользователя. '''
    # Создание клавиатуры с опцией "Да" и "Нет"
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Да", {"command": "/get_user_info"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("Нет", {"command": "/exit"}), color=KeyboardButtonColor.NEGATIVE)
    ).get_json()
    # Отправка приветственного сообщения и отображение клавиатуры
    await message.answer("Привет. Ищешь пару?", keyboard=keyboard)


# Определение обработчика для команды "/get_user_info"
@bot.on.message(payload={"command": "/get_user_info"})
async def get_user_info_handler(message: Message):
    ''' Обработчик-функция для сбора данных от пользователя. '''
    # Создание клавиатуры с опциями "Покажи" и "Выход"
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Покажи", {"command": "/show_candidate"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("Выход", {"command": "/exit"}), color=KeyboardButtonColor.NEGATIVE)
    ).get_json()

    # Получение данных о пользователе и создание объекта пользователя
    user_data = await bot.api.users.get(message.from_id, fields=["city", "sex", "bdate"])
    user = await _make_user(user_data)

    # Добавление пользователя в базу данных и сохранение изменений
    db_interaction.add_person_to_db(user)
    db_interaction.commit_session()
    ctx_storage.set(f"offset_{message.from_id}", 0)

    # Отправка сообщения о начале поиска и отображение клавиатуры
    await message.answer("Начинаю поиск...", keyboard=keyboard)


# Определение обработчика для команды "/show_candidate"
@bot.on.message(payload={"command": "/show_candidate"})
async def show_candidate_handler(message: Message):
    ''' Обработчик-функция для поиска кандидата и отправки данных о кандидате пользователю. '''
    # Создание клавиатуры с различными опциями
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Покажи", {"command": "/show_candidate"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("Добавить в избранные", {"command": "/favourite_add"}), color=KeyboardButtonColor.PRIMARY)
        .add(Text("Список избранных", {"command": "/favourite_list"}), color=KeyboardButtonColor.SECONDARY)
        .add(Text("Выход", {"command": "/exit"}), color=KeyboardButtonColor.NEGATIVE)
    ).get_json()

    # Получение смещения и информации о пользователе из хранилища контекста и базы данных
    offset = ctx_storage.get(f"offset_{message.from_id}")
    user = db_interaction.get_from_db(vk_id=message.from_id, model=User)

    # Поиск кандидата и обновление смещения
    candidate_from_vk, offset = await _candidate_search(user, offset)

    # Пока кандидат не имеет открытый доступ к информации, продолжаем поиск
    while not candidate_from_vk.can_access_closed:
        try:
            candidate_from_vk, offset = await _candidate_search(user, offset)
        except IndexError:
            offset = 0
            candidate_from_vk, offset = await _candidate_search(user)

    # Создание объекта кандидата и получение его фотографий
    candidate = await _make_candidate(candidate_from_vk, message.from_id)
    photos = await _get_photos(candidate_from_vk.id)
    top3_photo = await _get_top3_photo(photos)

    # Добавление кандидата и его фотографий в базу данных
    db_interaction.add_person_to_db(candidate)
    db_interaction.commit_session()

    for photo_data in top3_photo:
        # Создание объектов фотографий и добавление их в базу данных
        photo = await _make_photo(photo_data, candidate.vk_id)
        db_interaction.add_photos_to_db(photo)
        db_interaction.commit_session()

    # Обновление смещения и сохранение информации о кандидате в хранилище контекста
    ctx_storage.set(f"offset_{message.from_id}", offset)
    ctx_storage.set(f"candidate_{message.from_id}", candidate)

    # Отправка информации о кандидате пользователю
    await message.answer(f"{candidate.first_name} {candidate.last_name}\n{candidate.vk_link}",
                         attachment=top3_photo, keyboard=keyboard)


# Определение обработчика для команды "/favourite_add"
@bot.on.message(payload={"command": "/favourite_add"})
async def favourite_add_handler(message: Message):
    ''' Обработчик-функция для добавления кандидата в избранное. '''
    # Создание клавиатуры с опциями "Покажи ещё" и "Выход"
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Покажи ещё", {"command": "/show_candidate"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("Выход", {"command": "/exit"}), color=KeyboardButtonColor.NEGATIVE)
    ).get_json()
    # Получение информации о кандидате из хранилища контекста
    candidate = ctx_storage.get(f"candidate_{message.from_id}")
    # Изменение статуса кандидата на "избранный" в базе данных
    db_interaction.change_is_favourite(candidate.vk_id)
    # Отправка сообщения пользователю об успешном добавлении кандидата в избранное
    await message.answer(f"Добавил {candidate.first_name} {candidate.last_name} в избранные", keyboard=keyboard)


# Определение обработчика для команды "/favourite_list"
@bot.on.message(payload={"command": "/favourite_list"})
async def favourite_list_handler(message: Message):
    ''' Обработчик-функция для отображения списка избранных. '''
    # Создание клавиатуры с опциями "Покажи ещё" и "Выход"
    keyboard = (
        Keyboard(one_time=True, inline=False)
        .add(Text("Покажи ещё", {"command": "/show_candidate"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("Выход", {"command": "/exit"}), color=KeyboardButtonColor.NEGATIVE)
    ).get_json()
    # Получение списка кандидатов из избранных из базы данных
    candidates = db_interaction.show_favourite_list()

    for candidate in candidates:
        # Отображение списка избранных кандидатов пользователю
        await message.answer(
            f"Вот список избранных:\n{candidate[0].first_name} {candidate[0].last_name}\n{candidate[0].vk_link}\n",
            attachment=[photo.vk_link for photo in candidate[1]], keyboard=keyboard)
        # Пауза для предотвращения засорения чата
        sleep(0.5)


# Определение обработчика для команды "/exit"
@bot.on.message(payload={"command": "/exit"})
async def exit_handler(message: Message):
    ''' Обработчик-функция для прощания с пользователем. '''
    # Закрытие сессии базы данных
    db_interaction.close_session()
    # Отправка сообщения с прощанием пользователю и предложением начать снова
    await message.answer("Жаль, что ты уходишь. Приходи ещё. Чтобы начать снова напиши /start", keyboard=EMPTY_KEYBOARD)


# Определение общего обработчика для сообщений
@bot.on.message()
async def echo_handler(message: Message):
    ''' Простая обработчик-функция с логикой эхо. '''
    # Отправка эхо-сообщения пользователю
    await message.answer("Я всего лишь бот. Я не могу понять такие сложные вещи. Напиши /start, чтобы магия началась.")
