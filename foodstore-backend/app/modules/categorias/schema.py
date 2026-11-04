from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


# 1. Atributos base compartidos
class CategoriaBase(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)


# 2. Esquema de entrada para CREAR (POST)
class CategoriaCreate(CategoriaBase):
    """Datos que envía el cliente para crear una nueva categoría."""
    pass


# 3. Esquema de entrada para ACTUALIZAR (PUT)
class CategoriaUpdate(SQLModel):
    """Datos que envía el cliente para actualizar nombre y descripción."""
    nombre: str = Field(min_length=3, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)


# 4. Esquema de salida para RESPONDER (GET / POST / PUT)
class CategoriaRead(CategoriaBase):
    """Datos que el backend devuelve al cliente en formato JSON."""
    id: int
    activo: bool
    anulado_at: Optional[datetime] = None

