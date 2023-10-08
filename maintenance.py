# Скрипт с внутренней логикой бота для поиска кандидатов для романтических свиданий

# Импорт модуля datetime с псевдонимом dt
import datetime as dt
from typing import List

from config import USER_TOKEN
# Импорт класса API из библиотеки vkbottle и токена пользователя из конфигурационного файла
from vkbottle import API

# Импорт пользовательских моделей User, Candidate, Photo
from models import User, Candidate, Photo

# Создание объекта API для работы с VK API
user_api = API(USER_TOKEN)


def _string_with_born_to_age(born: str) -> int:
    ''' Функция принимает дату рождения в виде строки и возвращает возраст в виде целого числа '''
    # Получение текущей даты
    today = dt.date.today()
    # Преобразование строки с датой рождения в объект datetime
    born_date = dt.datetime.strptime(born, "%d.%m.%Y")
    # Расчет возраста
    return today.year - born_date.year - ((today.month, today.day) < (
        born_date.month, born_date.day))


def _get_opposite_sex(sex_id: int) -> int:
    ''' Функция принимает идентификатор пола и возвращает противоположный идентификатор (согласно документации VK API) '''
    return 1 if sex_id == 2 else 2


async def _make_user(user_data) -> User:
    ''' Функция возвращает объект класса User '''
    return User(vk_id=user_data[0].id,
                first_name=user_data[0].first_name,
                last_name=user_data[0].last_name,
                age=_string_with_born_to_age(user_data[0].bdate),
                sex_id=user_data[0].sex.value,
                city_id=user_data[0].city.id)


async def _candidate_search(user, offset) -> tuple:
    ''' Функция принимает данные для поиска кандидата и номер смещения в поиске,
     возвращает кортеж с данными о кандидате и номером смещения '''
    # Поиск кандидата
    candidate = await user_api.users.search(age_from=user.age - 5,
                                            age_to=user.age + 5,
                                            sex=_get_opposite_sex(user.sex_id),
                                            city=user.city_id,
                                            count=1,
                                            offset=offset,
                                            fields=["can_access_closed"])

    return (candidate.items[0], offset + 1)


async def _make_candidate(candidate, user_vk_id: int) -> Candidate:
    ''' Функция возвращает объект класса Candidate '''
    return Candidate(vk_id=candidate.id,
                     first_name=candidate.first_name,
                     last_name=candidate.last_name,
                     vk_link=f"https://vk.com/id{candidate.id}",
                     is_favourite=False,
                     user_vk_id=user_vk_id)


async def _get_photos(candidate_vk_id: int) -> list:
    ''' Функция принимает vk id пользователя и возвращает список с данными о фотоальбоме пользователя '''
    # Получение данных о фотографиях пользователя
    photos = await user_api.photos.get(owner_id=candidate_vk_id,
                                       album_id="profile",
                                       extended=True)
    return photos.items


async def _get_top3_photo(photos: list) -> List[str]:
    ''' Функция принимает список с данными о фотоальбоме пользователя и возвращает список трех элементов с данными для отправки фотографий в чат VK '''
    # Выбор топ-3 фотографий по количеству лайков
    top3_photo = sorted(photos, key=lambda photo: photo.likes.count)[-1:-4:-1]
    # Формирование списка с данными для отправки фотографий
    return [
        f"photo{photo.owner_id}_{photo.id}_{photo.access_key}"
        if photo.access_key is not None
        else f"photo{photo.owner_id}_{photo.id}" for photo in top3_photo
    ]


async def _make_photo(vk_link: str, candidate_vk_id: int) -> Photo:
    ''' Функция возвращает объект класса Photo '''
    return Photo(vk_link=vk_link, candidate_vk_id=candidate_vk_id)
