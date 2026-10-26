import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.database import engine, SessionLocal, Base
from app.data.models import Profession, Health, Hobby, Phobia, Luggage, Fact
from sqlalchemy import text

def seed_database():
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Принудительно устанавливаем кодировку UTF-8 для сессии PostgreSQL
        db.execute(text("SET client_encoding = 'utf8';"))
        
        if db.query(Profession).first():
            print("База данных уже содержит данные. Пропускаем сидирование.")
            return

        print("Заполнение базы данных тестовыми карточками на русском языке...")
        
        db.add_all([
            Profession(name="Инженер-программист"),
            Profession(name="Врач-хирург"),
            Profession(name="Повар"),
            Profession(name="Электрик"),
            Profession(name="Агроном")
        ])

        db.add_all([
            Health(name="Абсолютно здоров"),
            Health(name="Хроническая астма"),
            Health(name="Слабое зрение"),
            Health(name="Легкая глухота")
        ])

        db.add_all([
            Hobby(name="Выращивание растений"),
            Hobby(name="Выживание в дикой природе"),
            Hobby(name="Альпинизм"),
            Hobby(name="Радиоэлектроника")
        ])

        db.add_all([
            Phobia(name="Клаустрофобия"),
            Phobia(name="Арахнофобия"),
            Phobia(name="Боязнь темноты"),
            Phobia(name="Акрофобия (высота)")
        ])

        db.add_all([
            Luggage(name="Аптечка первой помощи"),
            Luggage(name="Многофункциональный нож"),
            Luggage(name="Семена овощей"),
            Luggage(name="Фильтр для воды")
        ])

        db.add_all([
            Fact(text="Бывший военный сапер"),
            Fact(text="Умеет играть на гитаре"),
            Fact(text="Владеет тремя языками"),
            Fact(text="Имеет черный пояс по карате")
        ])

        db.commit()
        print("База данных успешно заполнена русскими текстами!")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при заполнении базы: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()