from sqlalchemy import Column, Integer, String
from app.data.database import Base

class Profession(Base):
    __tablename__ = "professions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Health(Base):
    __tablename__ = "health_conditions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Hobby(Base):
    __tablename__ = "hobbies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Phobia(Base):
    __tablename__ = "phobias"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Luggage(Base):
    __tablename__ = "luggage"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True)