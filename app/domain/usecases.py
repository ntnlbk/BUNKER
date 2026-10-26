import random
from app.domain.interfaces import CardRepositoryProtocol
from app.domain.entities import PlayerCard  # Импортируем наш класс

class CreatePlayerCardUseCase:
    def __init__(self, repository: CardRepositoryProtocol):
        self.repository = repository

    def execute(self) -> PlayerCard:  # Указываем, что возвращаем объект PlayerCard
        # 1. Генерация случайных параметров
        gender = random.choice(["Мужской", "Женский"])
        age = random.randint(18, 75)
        experience = random.randint(0, 40)

        # 2. Получение характеристик из репозитория
        profession = self.repository.get_random_profession()
        health = self.repository.get_random_health()
        hobby = self.repository.get_random_hobby()
        phobia = self.repository.get_random_phobia()
        luggage = self.repository.get_random_luggage()
        fact_1 = self.repository.get_random_fact()
        fact_2 = self.repository.get_random_fact()

        # 3. Возвращаем готовый объект класса PlayerCard
        return PlayerCard(
            profession=profession,
            gender=gender,
            age=age,
            work_experience=experience,
            health=health,
            hobby=hobby,
            phobia=phobia,
            luggage=luggage,
            fact_1=fact_1,
            fact_2=fact_2
        )