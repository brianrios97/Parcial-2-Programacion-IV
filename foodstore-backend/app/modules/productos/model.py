from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime

if TYPE_CHECKING:
    from app.modules.unidades_medida.model import UnidadMedida


class Producto(SQLModel, table=True):
    """
    Entidad Producto: Representa los artículos del catálogo de Food Store.
    
    Reglas y restricciones:
    - unidad_venta_id: FK hacia UnidadMedida (obligatorio).
    - nombre: Obligatorio, mínimo 3 caracteres, único entre productos activos (RN-02).
    - precio_base: Numérico >= 0.
    - stock_cantidad: Numérico >= 0, medido en la unidad de venta (RN-10).
    - disponible: Booleano para pausar venta manualmente, independiente de activo (RN-12).
    - activo: Booleano para baja lógica (RN-04).
    - anulado_at: Timestamp con zona horaria que indica cuándo se dio de baja lógica.
    """
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    unidad_venta_id: int = Field(foreign_key="unidades_medida.id", nullable=False, index=True)
    nombre: str = Field(nullable=False, max_length=150, index=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio_base: float = Field(default=0.0, nullable=False, ge=0)
    stock_cantidad: float = Field(default=0.0, nullable=False, ge=0)
    disponible: bool = Field(default=True, nullable=False)
    activo: bool = Field(default=True, nullable=False)
    anulado_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Relación 1:N bidireccional con UnidadMedida
    unidad_venta: Optional["UnidadMedida"] = Relationship(back_populates="productos")

