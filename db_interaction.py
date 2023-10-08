# Скрипт с логикой взаимодействия с базой данных

# Импорт библиотеки sqlalchemy для работы с базой данных
import sqlalchemy as sq
from config import DB_LOGIN
from sqlalchemy.orm import sessionmaker

# Импорт пользовательских модулей для создания таблиц и определения сущностей
from models import create_tables, User, Candidate, Photo

# Формирование строки подключения к базе данных
DSN = f'postgresql://{DB_LOGIN["login"]}:{DB_LOGIN["password"]}@{DB_LOGIN["host"]}:{DB_LOGIN["port"]}/{DB_LOGIN["database"]}'

# Создание подключения к базе данных
engine = sq.create_engine(DSN)

# Создание таблиц в базе данных
create_tables(engine)

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


def _check_is_in_db(item):
    '''Проверка, есть ли пользователь/кандидат/фото в базе данных'''
    if isinstance(item, User):
        for user in session.query(User).all():
            if user.vk_id == item.vk_id:
                return True
    elif isinstance(item, Candidate):
        for candidate in session.query(Candidate).all():
            if candidate.vk_id == item.vk_id:
                return True
    elif isinstance(item, Photo):
        for photo in session.query(Photo).all():
            if photo.vk_link == item.vk_link:
                return True
    return False


def add_person_to_db(person):
    '''Добавление пользователя/кандидата в базу данных'''
    if _check_is_in_db(person):
        session.close()
        return
    session.add(person)


def add_photos_to_db(photo: Photo):
    '''Добавление фотографий кандидата в базу данных'''
    if _check_is_in_db(photo):
        return
    session.add(photo)


def show_favourite_list() -> list:
    '''Получение списка избранных кандидатов'''
    fav_list = []
    for c_ in session.query(Candidate).join(Photo.candidate). \
            filter(Candidate.is_favourite):
        photo_list = []
        for p_ in session.query(Photo).join(Candidate.photos). \
                filter(Photo.candidate_vk_id == c_.vk_id):
            photo_list.append(p_)
        fav_list.append([c_, photo_list])
    return fav_list


def get_from_db(vk_id: int, model):
    '''Получение объекта из базы данных'''
    return session.query(model).filter(model.vk_id == vk_id).first()


def change_is_favourite(vk_id: int):
    '''Добавление/удаление кандидата в/из избранных'''
    candidate = session.query(Candidate).filter(Candidate.vk_id == vk_id)
    if not candidate.first().is_favourite:
        candidate.update({Candidate.is_favourite: True})
    else:
        candidate.update({Candidate.is_favourite: False})
    session.commit()


def commit_session():
    '''Сохранение всех изменений в базу данных'''
    session.commit()


def close_session():
    '''Закрытие сессии'''
    session.close()
