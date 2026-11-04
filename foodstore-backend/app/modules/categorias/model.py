from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Categoria(SQLModel, table=True):
    """
    Entidad Categoria: Agrupa productos en rubros del menú de Food Store.
    Aplica baja lógica con 'activo' y 'anulado_at' (nunca se borra físicamente).
    """
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)

    # Campos de Baja Lógica (Soft Delete)
    activo: bool = Field(default=True, nullable=False, index=True)
    anulado_at: Optional[datetime] = Field(default=None, nullable=True)

