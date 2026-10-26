import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://root:root@postgres_db:5432/bunker_db"
)

def create_db_engine_with_retry(url, retries=5, delay=3):
    for i in range(retries):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Успешное подключение к базе данных!")
            return engine
        except OperationalError as e:
            print(f"База данных еще не готова (попытка {i+1}/{retries}). Ошибка: {e}")
            if i < retries - 1:
                time.sleep(delay)
            else:
                raise e

engine = create_db_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()