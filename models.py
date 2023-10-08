# Скрипт с моделями для базы данных

# Импорт библиотеки sqlalchemy с псевдонимом sq
import sqlalchemy as sq
from sqlalchemy.orm import relationship, declarative_base

# Создание базового класса для моделей
Base = declarative_base()


def create_tables(engine):
    ''' Функция для создания таблиц в базе данных '''
    # Создание таблиц на основе метаданных
    Base.metadata.create_all(engine)


class User(Base):
    ''' Модель Пользователя, взаимодействующего с ботом '''
    __tablename__ = 'user'

    # Определение столбцов таблицы
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.VARCHAR(1500))
    last_name = sq.Column(sq.VARCHAR(50))
    age = sq.Column(sq.SmallInteger)
    sex_id = sq.Column(sq.SmallInteger)
    city_id = sq.Column(sq.VARCHAR(25))

    def __str__(self):
        ''' Метод для представления объекта в виде строки '''
        return [self.id, self.vk_id,
                self.first_name, self.last_name,
                self.age, self.sex_id, self.city_id]


class Candidate(Base):
    ''' Модель Кандидата, найденного ботом '''
    __tablename__ = 'candidate'

    # Определение столбцов таблицы
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.VARCHAR(1500))
    last_name = sq.Column(sq.VARCHAR(50))
    vk_link = sq.Column(sq.VARCHAR(200))
    is_favourite = sq.Column(sq.Boolean)
    user_vk_id = sq.Column(
        sq.Integer,
        sq.ForeignKey("user.vk_id"),
        nullable=False
    )

    user = relationship('User', backref='candidates')

    def __str__(self):
        ''' Метод для представления объекта в виде строки '''
        return [self.id, self.vk_id, self.first_name,
                self.last_name]


class Photo(Base):
    ''' Модель фотографии кандидата '''
    __tablename__ = 'photo'

    # Определение столбцов таблицы
    id = sq.Column(sq.Integer, primary_key=True)
    vk_link = sq.Column(sq.String, unique=True)
    candidate_vk_id = sq.Column(
        sq.Integer,
        sq.ForeignKey("candidate.vk_id"),
        nullable=False
    )

    candidate = relationship('Candidate', backref='photos')

    def __str__(self):
        ''' Метод для представления объекта в виде строки '''
        return [self.id, self.vk_link,
                self.candidate_vk_id]
