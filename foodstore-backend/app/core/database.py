import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

# 1. Cadena de conexión leída desde variable de entorno
# Soporta PostgreSQL o SQLite como fallback local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodstore_p2.db")

# 2. Configuración para SQLite (solo si se usa SQLite en desarrollo)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# 3. El Motor (Engine): administra el pool de conexiones
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args
)


def create_db_and_tables() -> None:
    """Crea en la base de datos todas las tablas de los modelos que tengan table=True."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Abre una sesión de base de datos por petición HTTP y garantiza su cierre al terminar.
    Inyectable en routers mediante Depends(get_session).
    """
    with Session(engine) as session:
        yield session

