from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from app.modules.productos_categorias.model import ProductoCategoria


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

    # Relación N:N con Producto a través del link model ProductoCategoria
    productos: List["Producto"] = Relationship(  # type: ignore[name-defined]
        back_populates="categorias",
        link_model=ProductoCategoria
    )
