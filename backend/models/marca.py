from sqlalchemy import Column, Integer, Text

from database import Base


class Marca(Base):
    __tablename__ = "marca"

    id_marca = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, unique=True, nullable=False)
