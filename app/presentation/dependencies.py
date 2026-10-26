from app.data.repositories import PostgresCardRepository
from app.domain.interfaces import CardRepositoryProtocol

def get_card_repository() -> CardRepositoryProtocol:
    """
    Эта функция возвращает конкретную реализацию репозитория (PostgresCardRepository),
    но с точки зрения типов возвращает абстрактный интерфейс (CardRepositoryProtocol).
    
    Благодаря этому FastAPI может легко внедрить этот репозиторий через Depends().
    """
    return PostgresCardRepository()