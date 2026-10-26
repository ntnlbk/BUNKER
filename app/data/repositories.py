from sqlalchemy.sql import func
from app.data.database import SessionLocal
from app.data.models import Profession, Health, Hobby, Phobia, Luggage, Fact

class PostgresCardRepository:
    """Реализация репозитория карточек для PostgreSQL.
       Этот класс знает всё о том, как делать запросы в базу данных.
    """

    def _get_random_item(self, model, column_name="name"):
        """Вспомогательный метод: открывает сессию, берет случайную строку из таблицы и закрывает сессию."""
        db = SessionLocal()
        try:
            # func.random() заставляет PostgreSQL выбрать случайную строку
            item = db.query(model).order_by(func.random()).first()
            if not item:
                return "Нет данных"
            return getattr(item, column_name)
        finally:
            db.close()

    def get_random_profession(self) -> str:
        return self._get_random_item(Profession, "name")

    def get_random_health(self) -> str:
        return self._get_random_item(Health, "name")

    def get_random_hobby(self) -> str:
        return self._get_random_item(Hobby, "name")

    def get_random_phobia(self) -> str:
        return self._get_random_item(Phobia, "name")

    def get_random_luggage(self) -> str:
        return self._get_random_item(Luggage, "name")

    def get_random_fact(self) -> str:
        # Для фактов колонка называется "text", а не "name"
        return self._get_random_item(Fact, "text")