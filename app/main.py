from fastapi import FastAPI, Depends # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from dataclasses import asdict  # <-- Импортируем asdict для превращения датакласса в словарь
from app.domain.interfaces import CardRepositoryProtocol
from app.domain.usecases import CreatePlayerCardUseCase
from app.domain.entities import PlayerCard
from app.presentation.dependencies import get_card_repository

app = FastAPI(title="Bunker Game API")

@app.get("/")
def read_root():
    return JSONResponse(
        content={"message": "Бэкенд игры Бункер запущен!"},
        media_type="application/json; charset=utf-8"
    )

@app.get("/generate-card")
def generate_card(
    repository: CardRepositoryProtocol = Depends(get_card_repository)
):
    """Эндпоинт для генерации случайной карточки игрока с гарантированным UTF-8"""
    use_case = CreatePlayerCardUseCase(repository=repository)
    
    # Получаем объект датакласса
    card_object = use_case.execute()
    
    # Превращаем объект в словарь и явно указываем charset=utf-8
    card_dict = asdict(card_object)
    
    return JSONResponse(
        content=card_dict, 
        media_type="application/json; charset=utf-8"
    )